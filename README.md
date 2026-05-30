# DHCP Spoofing Attack Lab

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-red)
![Lab](https://img.shields.io/badge/Environment-GNS3%20%7C%20IOSvL2-orange)
![Attack](https://img.shields.io/badge/Attack-DHCP%20Spoofing-purple)
![Status](https://img.shields.io/badge/Use-Controlled%20Lab-yellow)
![Security](https://img.shields.io/badge/Topic-Network%20Security-darkgreen)

## Aviso de uso responsable

Este proyecto fue desarrollado únicamente con fines educativos, académicos y de laboratorio controlado.

El script debe ejecutarse solamente en redes propias, laboratorios autorizados o entornos virtuales como GNS3, EVE-NG o PNETLab. No debe utilizarse en redes públicas, empresariales o de terceros sin autorización explícita.

---

## Archivos del repositorio

| Archivo                                                        | Descripción                                                                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [`dhcp-spoofing.py`](./dhcp-spoofing.py)                       | Script principal utilizado para ejecutar el servidor DHCP falso desde Kali Linux.                              |
| [`fake-dns.py`](./fake-dns.py)                                 | Servidor DNS falso de laboratorio para demostrar manipulación DNS después del DHCP Spoofing.                   |
| [`mitigacion-dhcp-spoofing.md`](./mitigacion-dhcp-spoofing.md) | Documento técnico con la mitigación general contra DHCP Spoofing usando DHCP Snooping.                         |
| [`README.md`](./README.md)                                     | Documentación principal del laboratorio, uso del script, evidencia esperada y flujo recomendado para el video. |

---

## Descripción

Este laboratorio demuestra un ataque **DHCP Spoofing**, donde una máquina atacante ejecuta un servidor DHCP falso dentro de la red local.

El objetivo del atacante es responder a solicitudes DHCP de la víctima y entregarle una configuración de red manipulada, por ejemplo:

* Dirección IP asignada por el atacante.
* Gateway falso apuntando hacia Kali.
* DNS falso apuntando hacia Kali.
* Dominio controlado dentro del laboratorio.

Cuando la víctima acepta la configuración del servidor DHCP falso, su tráfico puede ser redirigido, manipulado o controlado dentro del entorno de pruebas.

---

## Base del direccionamiento IP

El direccionamiento IP del laboratorio fue definido tomando como base la matrícula:

```text
20250845
```

Separando la matrícula en octetos, se obtuvo la dirección base:

```text
20.25.8.45
```

A partir de esta dirección se creó la red del laboratorio:

```text
20.25.8.0/24
```

---

## Objetivo del laboratorio

Demostrar cómo un atacante conectado a la misma red local puede levantar un servidor DHCP falso y entregar parámetros de red maliciosos a una víctima.

---

## Objetivo del script

El script [`dhcp-spoofing.py`](./dhcp-spoofing.py) permite:

* Escuchar solicitudes DHCP Discover y DHCP Request.
* Responder con DHCP Offer y DHCP ACK falsos.
* Asignar una IP desde un pool controlado por el atacante.
* Configurar a Kali como gateway falso.
* Configurar a Kali como DNS falso.
* Registrar en consola los clientes que recibieron ofertas DHCP.
* Demostrar el impacto de un servidor DHCP no autorizado.

---

## Topología utilizada

```text
                   +----------------+
                   |      R1        |
                   | 20.25.8.45     |
                   | DHCP legítimo  |
                   +-------+--------+
                           |
                           |
                    Gi0/0  |
                   +-------+--------+
                   |      SW-1      |
                   |    IOSvL2      |
                   +---+--------+---+
                       |        |
                 Gi0/1 |        | Gi0/2
                       |        |
              +--------+        +--------+
              |                          |
        +-----+-----+              +-----+-----+
        |   Kali    |              |    VPC    |
        |20.25.8.46 |              | DHCP      |
        +-----------+              +-----------+
```

---

## Direccionamiento IP del laboratorio

| Dispositivo | Rol                     | Interfaz |  Dirección IP | Descripción                      |
| ----------- | ----------------------- | -------- | ------------: | -------------------------------- |
| R1          | Gateway / DHCP legítimo | Fa0/0    | 20.25.8.45/24 | Router principal de la red       |
| Kali        | Atacante / DHCP falso   | eth0     | 20.25.8.46/24 | Máquina atacante                 |
| VPC         | Víctima                 | eth0     |          DHCP | Equipo que solicita dirección IP |
| SW-1        | Switch                  | Gi0/0    |           N/A | Conexión hacia R1                |
| SW-1        | Switch                  | Gi0/1    |           N/A | Conexión hacia Kali              |
| SW-1        | Switch                  | Gi0/2    |           N/A | Conexión hacia la víctima        |

---

## Configuración DHCP legítima en R1

Para que el laboratorio sea funcional, R1 debe tener un servidor DHCP legítimo.

En este caso, R1 entrega la IP `20.25.8.47` a la VPC.

```cisco
enable
configure terminal

interface fastEthernet0/0
description LAN_20250845
ip address 20.25.8.45 255.255.255.0
no shutdown

ip dhcp excluded-address 20.25.8.1 20.25.8.46
ip dhcp excluded-address 20.25.8.48 20.25.8.254

ip dhcp pool LAN_20250845
network 20.25.8.0 255.255.255.0
default-router 20.25.8.45
dns-server 20.25.8.45
domain-name lab20250845.local
lease 0 1

end
write memory
```

---

## Configuración IP de Kali

Kali debe tener IP fija dentro de la red del laboratorio.

Si la interfaz del laboratorio es `eth0`:

```bash
sudo ip addr flush dev eth0
sudo ip addr add 20.25.8.46/24 dev eth0
sudo ip link set eth0 up
sudo ip route replace default via 20.25.8.45
```

Si la interfaz usada es otra, reemplazar `eth0` por la interfaz correcta.

---

## Prueba del DHCP legítimo

Antes del ataque, la VPC debe recibir DHCP desde R1.

En la VPC:

```text
clear ip
dhcp
show ip
```

Resultado esperado:

```text
IP/MASK     : 20.25.8.47/24
GATEWAY     : 20.25.8.45
DNS         : 20.25.8.45
DHCP SERVER : 20.25.8.45
DOMAIN NAME : lab20250845.local
```

---

## Requisitos

### Sistema atacante

* Kali Linux
* Python 3
* Scapy instalado
* Permisos de superusuario
* Conectividad directa de capa 2 con la víctima
* Interfaz conectada a la red del laboratorio

### Dispositivos de red

* Router Cisco o dispositivo gateway
* Switch IOSvL2, Ethernet switch o equivalente
* Cliente DHCP en la misma red local

---

## Verificar Scapy

Antes de ejecutar el script, validar que Scapy está disponible:

```bash
python3 -c "import scapy; print('Scapy instalado')"
```

Si Scapy no está instalado y Kali tiene internet:

```bash
sudo apt update
sudo apt install -y python3-scapy
```

---

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/iClexi/DHCP-Spoofing-Attack.git
cd DHCP-Spoofing-Attack
```

Dar permisos de ejecución:

```bash
chmod +x dhcp-spoofing.py
```

Verificar sintaxis:

```bash
python3 -m py_compile dhcp-spoofing.py
```

---

## Uso básico

Ejecutar el servidor DHCP falso:

```bash
sudo python3 dhcp-spoofing.py
```

El script solicitará la interfaz conectada a la red víctima.

Ejemplo:

```text
Interfaces disponibles:

1. eth0 UP 20.25.8.46/24
2. eth1 DOWN

Interfaz conectada a la red víctima [Enter = eth0]:
```

---

## Uso directo por parámetros

Ejecutar el ataque indicando todos los parámetros:

```bash
sudo python3 dhcp-spoofing.py -i eth0 \
  --server-ip 20.25.8.46 \
  --gateway 20.25.8.46 \
  --dns 20.25.8.46 \
  --pool 20.25.8.100-20.25.8.200 \
  --yes
```

---

## Parámetros disponibles

| Parámetro       | Descripción                               |                  Valor por defecto |
| --------------- | ----------------------------------------- | ---------------------------------: |
| `-i`, `--iface` | Interfaz conectada a la red víctima       |                Pregunta al usuario |
| `--server-ip`   | IP usada por el servidor DHCP falso       |                       `20.25.8.46` |
| `--gateway`     | Gateway entregado a la víctima            |                       `20.25.8.46` |
| `--dns`         | DNS entregado a la víctima                |                       `20.25.8.46` |
| `--subnet-mask` | Máscara de red entregada                  |                    `255.255.255.0` |
| `--pool`        | Rango de IPs falsas entregadas a clientes |          `20.25.8.100-20.25.8.200` |
| `--exclude`     | IPs que no deben ser entregadas           | `20.25.8.45,20.25.8.46,20.25.8.47` |
| `--lease-time`  | Tiempo de concesión DHCP en segundos      |                             `3600` |
| `--domain`      | Dominio entregado por DHCP                |                        `lab.local` |
| `--yes`         | Ejecuta sin pedir confirmación adicional  |                        Desactivado |

---

## Funcionamiento técnico

El ataque se basa en el proceso DHCP conocido como DORA:

```text
Discover -> Offer -> Request -> Acknowledge
```

El cliente envía un mensaje **DHCP Discover** buscando un servidor DHCP.

El servidor falso en Kali responde con un **DHCP Offer** ofreciendo una IP controlada por el atacante.

Luego, si el cliente acepta la oferta, Kali responde con un **DHCP ACK** confirmando la configuración.

---

## Configuración entregada por el servidor falso

Ejemplo de configuración maliciosa entregada a la víctima:

```text
IP asignada:       20.25.8.100
Gateway falso:     20.25.8.46
DNS falso:         20.25.8.46
Servidor DHCP:     20.25.8.46
Máscara:           255.255.255.0
Dominio:           lab.local
```

En este escenario, Kali no entrega su propia IP como IP del cliente. Kali entrega una IP del pool falso y se anuncia como gateway y DNS.

---

## Evidencia esperada del ataque

En Kali se debe observar:

```text
OFFER enviado -> cliente=00:50:79:66:68:00 ip=20.25.8.100 gateway=20.25.8.46 dns=20.25.8.46
ACK enviado -> cliente=00:50:79:66:68:00 ip=20.25.8.100 gateway=20.25.8.46 dns=20.25.8.46
```

En la VPC se debe observar:

```text
IP/MASK     : 20.25.8.100/24
GATEWAY     : 20.25.8.46
DNS         : 20.25.8.46
DHCP SERVER : 20.25.8.46
```

Esto confirma que la víctima recibió configuración desde un servidor DHCP falso.

---

## Captura con tcpdump

En Kali, se puede capturar el proceso DHCP:

```bash
sudo tcpdump -i eth0 -n -e "udp and (port 67 or port 68)"
```

Se espera observar tráfico DHCP Discover, Offer, Request y ACK.

---

## Demostración adicional: DNS falso de laboratorio

Como el servidor DHCP falso entrega a Kali como DNS, se puede demostrar manipulación de resolución DNS usando un dominio local de laboratorio.

### 1. Crear una página web de prueba en Kali

```bash
mkdir -p ~/dns-demo
cd ~/dns-demo
echo "<h1>DNS Spoofing Demo</h1><p>Pagina servida desde Kali 20.25.8.46</p>" > index.html
sudo python3 -m http.server 80 --bind 20.25.8.46
```

### 2. Ejecutar el DNS falso

```bash
chmod +x fake-dns.py
sudo python3 fake-dns.py --listen 20.25.8.46 --ip 20.25.8.46
```

Dominios de laboratorio soportados por defecto:

```text
demo.local
portal.lab
login.lab
```

### 3. Probar desde la víctima

En la VPC:

```text
ping demo.local
```

Resultado esperado en Kali:

```text
consulta=demo.local cliente=20.25.8.100
respuesta=demo.local -> 20.25.8.46
```

Esto demuestra que el atacante, al entregar un DNS falso por DHCP, puede controlar la resolución de nombres dentro del laboratorio.

---

## Mitigación

La mitigación recomendada contra DHCP Spoofing es:

```text
DHCP Snooping
```

La documentación completa de mitigación está disponible aquí:

* [`mitigacion-dhcp-spoofing.md`](./mitigacion-dhcp-spoofing.md)

---

## Configuración básica de mitigación

En esta topología:

```text
Gi0/0 -> R1 / DHCP legítimo
Gi0/1 -> Kali / DHCP falso
Gi0/2 -> VPC / Cliente DHCP
```

La configuración recomendada es:

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 1
no ip dhcp snooping information option

interface gigabitEthernet0/0
description Puerto_confiable_hacia_R1_DHCP_legitimo
ip dhcp snooping trust

interface gigabitEthernet0/1
description Puerto_no_confiable_hacia_Kali_DHCP_falso
no ip dhcp snooping trust

interface gigabitEthernet0/2
description Puerto_no_confiable_hacia_VPC_cliente
no ip dhcp snooping trust

end
write memory
```

---

## Verificación de la mitigación

En el switch:

```cisco
show ip dhcp snooping
show ip dhcp snooping binding
```

Después de aplicar la mitigación, ejecutar nuevamente el ataque y renovar DHCP en la víctima:

```text
clear ip
dhcp
show ip
```

Resultado esperado:

```text
IP/MASK     : 20.25.8.47/24
GATEWAY     : 20.25.8.45
DNS         : 20.25.8.45
DHCP SERVER : 20.25.8.45
```

La víctima debe recibir configuración únicamente del DHCP legítimo en R1.

---

## Flujo recomendado para el video

1. Mostrar la topología en GNS3.
2. Mostrar nombre, matrícula, fecha y hora.
3. Mostrar la configuración DHCP legítima de R1.
4. Mostrar que la VPC recibe DHCP legítimo desde `20.25.8.45`.
5. Ejecutar `dhcp-spoofing.py` desde Kali.
6. Renovar DHCP en la VPC.
7. Mostrar que la VPC recibió:

   * IP del pool falso.
   * Gateway `20.25.8.46`.
   * DNS `20.25.8.46`.
   * DHCP Server `20.25.8.46`.
8. Ejecutar `fake-dns.py`.
9. Mostrar resolución de `demo.local` hacia Kali.
10. Aplicar DHCP Snooping.
11. Renovar DHCP en la VPC.
12. Confirmar que la VPC vuelve a recibir DHCP legítimo desde R1.
13. Cerrar con una conclusión técnica.

---

## Troubleshooting

### La VPC sigue tomando DHCP desde R1

Esto puede pasar porque hay dos servidores DHCP compitiendo y la víctima acepta la primera oferta que recibe.

Para una demostración controlada, se puede apagar temporalmente el DHCP legítimo en R1:

```cisco
enable
configure terminal
no service dhcp
end
write memory
```

Después de la prueba, restaurar el servicio:

```cisco
enable
configure terminal
service dhcp
end
write memory
```

---

### Kali no ve las solicitudes DHCP de la VPC

Verificar la interfaz correcta:

```bash
ip -br a
```

Capturar tráfico DHCP:

```bash
sudo tcpdump -i eth0 -n -e "udp and (port 67 or port 68)"
```

Debe aparecer la MAC de la VPC.

---

### El DNS falso no responde

Verificar que la víctima recibió DNS de Kali:

```text
show ip
```

Debe mostrar:

```text
DNS : 20.25.8.46
```

Verificar que el DNS falso está escuchando en Kali:

```bash
sudo ss -ulpn | grep ':53'
```

---

## Estructura recomendada del repositorio

```text
DHCP-Spoofing-Attack/
├── README.md
├── dhcp-spoofing.py
├── fake-dns.py
├── mitigacion-dhcp-spoofing.md
├── captures/
│   ├── dhcp-legitimate.png
│   ├── dhcp-fake-offer.png
│   ├── dhcp-fake-result.png
│   ├── dns-fake-demo.png
│   └── mitigation.png
├── docs/
│   └── technical-report.md
└── video/
    └── youtube-link.txt
```

---

## Evidencias recomendadas

| Evidencia              | Descripción                                         |
| ---------------------- | --------------------------------------------------- |
| `dhcp-legitimate.png`  | VPC recibiendo DHCP legítimo desde R1               |
| `dhcp-fake-offer.png`  | Kali enviando DHCP Offer y ACK falsos               |
| `dhcp-fake-result.png` | VPC con gateway, DNS y DHCP server apuntando a Kali |
| `dns-fake-demo.png`    | Resolución de dominio de laboratorio hacia Kali     |
| `mitigation.png`       | DHCP Snooping aplicado y funcionando                |

---

## Topics sugeridos para GitHub

```text
dhcp
dhcp-spoofing
rogue-dhcp
kali-linux
python
scapy
gns3
iosvl2
network-security
cybersecurity
packet-crafting
lab
ethical-hacking
```

---

## Conclusión

Este laboratorio demuestra cómo un servidor DHCP falso puede entregar configuración de red manipulada a una víctima dentro de una red local.

El ataque fue validado al observar que la víctima recibió una dirección IP desde el pool falso y configuró como gateway, DNS y DHCP server a la máquina Kali.

También se demostró el impacto adicional de entregar un DNS falso mediante DHCP, resolviendo dominios de laboratorio hacia la IP del atacante.

La mitigación recomendada es aplicar **DHCP Snooping**, marcando como confiable únicamente el puerto hacia el servidor DHCP legítimo y dejando como no confiables los puertos de usuario.

Para más detalles, revisar el documento de mitigación:

* [`mitigacion-dhcp-spoofing.md`](./mitigacion-dhcp-spoofing.md)

---

## Autor

**Michael Robles / iClexi**
Laboratorio de Seguridad de Redes
Proyecto académico de ataque y mitigación DHCP Spoofing
