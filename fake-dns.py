#!/usr/bin/env python3
import argparse
import socket
import struct
import sys

def decode_qname(data, offset):
labels = []

```
while True:
    if offset >= len(data):
        raise ValueError("DNS query inválida")

    length = data[offset]

    if length == 0:
        offset += 1
        break

    offset += 1

    if offset + length > len(data):
        raise ValueError("DNS query inválida")

    labels.append(data[offset:offset + length].decode(errors="ignore"))
    offset += length

return ".".join(labels), offset
```

def make_response(query, response_ip, allowed_domains, ttl):
if len(query) < 12:
return None, None, "query demasiado corta"

```
transaction_id = query[:2]

flags = b"\x81\x80"
qdcount = query[4:6]
ancount = b"\x00\x01"
nscount = b"\x00\x00"
arcount = b"\x00\x00"

try:
    qname, offset = decode_qname(query, 12)
except Exception as e:
    return None, None, str(e)

if offset + 4 > len(query):
    return None, qname, "query incompleta"

qtype = query[offset:offset + 2]
qclass = query[offset + 2:offset + 4]
question = query[12:offset + 4]

domain = qname.lower().strip(".")
allowed = [d.lower().strip(".") for d in allowed_domains]

if domain not in allowed:
    return None, domain, "dominio no permitido"

if qtype != b"\x00\x01":
    return None, domain, "solo se responde tipo A"

if qclass != b"\x00\x01":
    return None, domain, "solo se responde clase IN"

answer_name = b"\xc0\x0c"
answer_type = b"\x00\x01"
answer_class = b"\x00\x01"
answer_ttl = struct.pack("!I", ttl)
answer_rdlength = struct.pack("!H", 4)
answer_rdata = socket.inet_aton(response_ip)

header = transaction_id + flags + qdcount + ancount + nscount + arcount
answer = (
    answer_name
    + answer_type
    + answer_class
    + answer_ttl
    + answer_rdlength
    + answer_rdata
)

return header + question + answer, domain, None
```

def parse_domains(value):
domains = []

```
for item in value.split(","):
    item = item.strip().lower().strip(".")

    if item:
        domains.append(item)

if not domains:
    print("Debes especificar al menos un dominio permitido")
    sys.exit(1)

return domains
```

def validate_ip(value, label):
try:
socket.inet_aton(value)
except Exception:
print(f"{label} inválida: {value}")
sys.exit(1)

def main():
parser = argparse.ArgumentParser(
description="DNS falso para laboratorio de DHCP Spoofing"
)

```
parser.add_argument("--listen", default="20.25.8.46")
parser.add_argument("--port", type=int, default=53)
parser.add_argument("--ip", default="20.25.8.46")
parser.add_argument("--domains", default="demo.local,portal.lab,login.lab")
parser.add_argument("--ttl", type=int, default=60)

args = parser.parse_args()

validate_ip(args.listen, "IP de escucha")
validate_ip(args.ip, "IP de respuesta")

if args.port < 1 or args.port > 65535:
    print("El puerto debe estar entre 1 y 65535")
    sys.exit(1)

if args.ttl < 0:
    print("El TTL no puede ser negativo")
    sys.exit(1)

domains = parse_domains(args.domains)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    sock.bind((args.listen, args.port))
except PermissionError:
    print("Ejecuta con sudo para usar el puerto 53")
    sys.exit(1)
except OSError as e:
    print(f"No pude iniciar DNS en {args.listen}:{args.port}: {e}")
    sys.exit(1)

print("")
print("DNS falso iniciado")
print(f"listen={args.listen}:{args.port}")
print(f"respuesta_ip={args.ip}")
print(f"dominios={', '.join(domains)}")
print(f"ttl={args.ttl}")
print("Usa Ctrl+C para detener")
print("")

queries = 0
responses = 0
ignored = 0

try:
    while True:
        data, addr = sock.recvfrom(512)
        queries += 1

        response, domain, reason = make_response(
            data,
            args.ip,
            domains,
            args.ttl
        )

        if domain:
            print(f"consulta={domain} cliente={addr[0]}:{addr[1]}")

        if response:
            sock.sendto(response, addr)
            responses += 1
            print(f"respuesta={domain} -> {args.ip}")
        else:
            ignored += 1

            if domain:
                print(f"ignorado={domain} razon={reason}")

except KeyboardInterrupt:
    print("")
    print("Finalizado")
    print(f"consultas={queries}")
    print(f"respuestas={responses}")
    print(f"ignoradas={ignored}")
finally:
    sock.close()
```

if **name** == "**main**":
main()
