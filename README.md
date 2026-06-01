# Ataque DHCP Spoofing

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-red)
![Environment](https://img.shields.io/badge/Environment-GNS3%20%7C%20IOSvL2-orange)
![Use](https://img.shields.io/badge/Use-Controlled%20Lab-yellow)
![Topic](https://img.shields.io/badge/Topic-Network%20Security-purple)

## Información del proyecto

Este repositorio documenta y demuestra un ataque de **DHCP Spoofing** dentro de un laboratorio controlado de seguridad de redes. El objetivo es mostrar cómo un atacante puede levantar un servidor DHCP falso en la misma red local y entregar a una víctima una configuración manipulada, incluyendo dirección IP, gateway y DNS controlados por el atacante.

La práctica también incluye una contramedida basada en **DHCP Snooping**, aplicada sobre el switch para bloquear respuestas DHCP provenientes de puertos no confiables.

| Dato | Información |
|---|---|
| Autor | Michael David Robles Fermín |
| Alias | iClexi |
| Matrícula | 2025-0845 |
| Repositorio | https://github.com/iClexi/DHCP-Spoofing-Attack |
| Video demostrativo | https://www.youtube.com/watch?v=8mBYpaTNwKk |
| Documentación técnica | [docs/documentacion-tecnica-profesional.pdf](docs/documentacion-tecnica-profesional.pdf) |

## Aviso de uso responsable

Este proyecto fue desarrollado únicamente con fines educativos, académicos y de laboratorio controlado.

El script debe ejecutarse solamente en redes propias, laboratorios autorizados o entornos virtuales como GNS3, EVE-NG o PNETLab. No debe utilizarse en redes públicas, empresariales o de terceros sin autorización explícita.

## Objetivo del laboratorio

Demostrar cómo un servidor DHCP no autorizado puede entregar configuración de red falsa a una víctima, haciendo que esta utilice al atacante como gateway y servidor DNS. Esto permite controlar parte del tráfico de la víctima, alterar la resolución de nombres y redirigir consultas hacia servicios falsos dentro del laboratorio.

## Objetivo del script

El script `dhcp-spoofing.py` permite levantar un servidor DHCP falso desde Kali Linux. Su función principal es responder a solicitudes DHCP enviadas por clientes de la red y entregar una configuración manipulada.

El ataque se basa en el proceso DHCP DORA:

```text
Discover -> Offer -> Request -> Acknowledge
```

En este laboratorio, Kali responde con un **DHCP Offer** y un **DHCP ACK** maliciosos, asignando como gateway y DNS la IP del atacante:

```text
20.25.8.46
```

## Archivos del repositorio

| Archivo | Descripción |
|---|---|
| `dhcp-spoofing.py` | Script principal para ejecutar el servidor DHCP falso. |
| `fake-dns.py` | Script de DNS falso usado para responder dominios controlados en el laboratorio. |
| `mitigacion-dhcp-spoofing.md` | Documento con contramedidas contra DHCP Spoofing. |
| `README.md` | Guía principal tipo how-to del laboratorio. |
| `docs/documentacion-tecnica-profesional.pdf` | Documentación técnica profesional detallada del ataque. |
| `images/` | Carpeta con capturas de evidencia usadas en esta guía. |

## Topología del laboratorio

La topología utilizada está compuesta por un router R-1, un switch SW-1, una máquina Kali Linux atacante y una víctima PC1/VPCS.

![Topología del laboratorio](images/topology.png)

| Dispositivo | Rol | Interfaz | Dirección IP | Descripción |
|---|---|---|---|---|
| R-1 | Gateway / DHCP legítimo | F0/0 | 20.25.8.45/24 | Router principal y servidor DHCP legítimo. |
| SW-1 | Switch de capa 2 | e0/e1/e2 | N/A | Switch que conecta todos los equipos. |
| Kali Linux | Atacante | eth0 | 20.25.8.46/24 | Equipo que ejecuta DHCP falso, DNS falso y página falsa. |
| PC1 / VPCS | Víctima | e0 | DHCP | Cliente que recibe configuración manipulada. |

## Requisitos previos

- GNS3 o entorno equivalente.
- Router Cisco con DHCP configurado.
- Switch Cisco IOSvL2 o switch compatible.
- Kali Linux con Python 3.
- Permisos de superusuario en Kali.
- Conectividad de capa 2 entre Kali, PC1 y R-1.
- Scripts `dhcp-spoofing.py` y `fake-dns.py` disponibles en el repositorio.

## Configuración básica del DHCP legítimo

Antes del ataque, R-1 funciona como servidor DHCP legítimo de la red. Esta configuración permite que los clientes reciban una dirección IP válida, gateway y DNS desde el router.

```cisco
service dhcp

interface fastEthernet0/0
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
```

![Configuración DHCP básica en R-1](images/router_dhcp_before.png)

## Instalación y preparación

Clonar el repositorio:

```bash
git clone https://github.com/iClexi/DHCP-Spoofing-Attack.git
cd DHCP-Spoofing-Attack
```

Verificar Python 3:

```bash
python3 --version
```

Ejecutar los scripts con permisos administrativos:

```bash
sudo python3 dhcp-spoofing.py
```

## Ejecución del ataque DHCP Spoofing

Desde Kali Linux se ejecuta el script principal:

```bash
sudo python3 dhcp-spoofing.py
```

El script solicita la interfaz conectada a la red víctima. En este laboratorio se utiliza `eth0`, con la dirección IP `20.25.8.46/24`.

La configuración maliciosa utilizada por el servidor DHCP falso es:

| Parámetro | Valor |
|---|---|
| Servidor DHCP falso | 20.25.8.46 |
| Gateway entregado | 20.25.8.46 |
| DNS entregado | 20.25.8.46 |
| Rango falso | 20.25.8.100 - 20.25.8.200 |
| Máscara | 255.255.255.0 |
| Dominio | lab.local |

![Ejecución del script DHCP Spoofing](images/script_execution.png)

## DHCP exitoso en PC1 con servidor malicioso

Luego de ejecutar el servidor DHCP falso, PC1 solicita una dirección IP mediante DHCP.

```text
dhcp
show ip
```

La víctima recibe configuración desde Kali, usando al atacante como gateway:

```text
DORA IP 20.25.8.100/24 GW 20.25.8.46
```

![PC1 recibe DHCP desde el servidor malicioso](images/pc1_dhcp_spoofed.png)

## Evidencia del proceso DORA malicioso

En Kali se observa el proceso DORA ejecutado por el servidor DHCP falso:

```text
OFFER enviado
ACK enviado
```

Esto confirma que Kali respondió a la víctima y entregó una configuración de red manipulada.

![DORA correcto desde servidor malicioso](images/dhcp_offer_ack.png)

## Creación de una página falsa

Aprovechando que la víctima recibió como DNS la IP del atacante, se levanta una página web falsa en Kali.

Primero se crea el contenido HTML:

```bash
mkdir dns-demo
cd dns-demo
echo "<h1>DNS Spoofing Demo</h1><p>Pagina servida desde Kali 20.25.8.46</p>" > index.html
```

Luego se ejecuta un servidor HTTP en el puerto 80:

```bash
sudo python3 -m http.server 80 --bind 20.25.8.46
```

![Página falsa servida desde Kali](images/fake_web_server.png)

## Listener DNS falso

Después se ejecuta el servidor DNS falso:

```bash
sudo python3 fake-dns.py --listen 20.25.8.46 --ip 20.25.8.46
```

El DNS falso responde dominios permitidos como:

```text
demo.local
portal.lab
login.lab
```

Cuando la víctima consulta `demo.local`, Kali responde con la IP del atacante:

```text
demo.local -> 20.25.8.46
```

![Listener DNS falso en Kali](images/fake_dns_running.png)

## Prueba de resolución hacia demo.local

Desde PC1 se prueba el dominio falso:

```text
ping demo.local
```

El resultado confirma que `demo.local` resuelve hacia `20.25.8.46`, es decir, hacia Kali.

![Ping hacia demo.local](images/dns_spoofing_query.png)

## Impacto del ataque

El ataque DHCP Spoofing permite que un cliente acepte configuración de red proveniente de un servidor no autorizado. En este laboratorio, la víctima termina utilizando a Kali como gateway y DNS.

Impactos observados:

- La víctima recibe una IP entregada por Kali.
- El gateway de la víctima apunta al atacante.
- El DNS de la víctima apunta al atacante.
- El atacante puede responder consultas DNS específicas.
- El atacante puede redirigir dominios como `demo.local` hacia una página falsa.

## Mitigación con DHCP Snooping

La contramedida principal aplicada es **DHCP Snooping** en el switch. Esta protección permite definir qué puertos son confiables para enviar respuestas DHCP.

En este laboratorio:

| Puerto | Dispositivo conectado | Estado DHCP Snooping |
|---|---|---|
| Gi0/0 | R-1 / DHCP legítimo | Trusted |
| Gi0/1 | Kali / DHCP falso | Untrusted |
| Gi0/2 | PC1 / Cliente | Untrusted |

Configuración aplicada en SW-1:

```cisco
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
```

![Aplicación de DHCP Snooping en el switch](images/mitigation_dhcp_snooping_config.png)

## Verificación posterior a la mitigación

Después de aplicar DHCP Snooping, se limpia la configuración IP de PC1 y se solicita DHCP nuevamente:

```text
clear ip
dhcp
```

El resultado esperado es que la víctima ya no acepte respuestas DHCP desde Kali. En la evidencia se observa que PC1 no encuentra un servidor DHCP falso disponible desde el puerto no confiable.

![PC1 no encuentra servidor DHCP después de la mitigación](images/pc1_dhcp_after_mitigation.png)

## Explicación técnica de la mitigación

DHCP Snooping protege la red al filtrar mensajes DHCP según el puerto por donde entran. Los mensajes DHCP Offer y DHCP ACK solo deben venir desde un servidor DHCP legítimo.

Por eso se marca como confiable el puerto hacia R-1:

```cisco
ip dhcp snooping trust
```

Y se dejan como no confiables los puertos hacia Kali y PC1:

```cisco
no ip dhcp snooping trust
```

De esta forma, aunque Kali mantenga el servidor DHCP falso activo, el switch bloquea sus respuestas porque provienen de un puerto no confiable.

## Video demostrativo

La demostración práctica del ataque y su mitigación está disponible en YouTube:

[Ver video del laboratorio en YouTube](https://www.youtube.com/watch?v=8mBYpaTNwKk)

URL directa:

```text
https://www.youtube.com/watch?v=8mBYpaTNwKk
```

## Documentación técnica profesional

Para una explicación más detallada del ataque, incluyendo objetivo del laboratorio, objetivo del script, funcionamiento técnico, parámetros, topología, evidencias y contramedidas, consultar el documento:

[Ver documentación técnica profesional](docs/documentacion-tecnica-profesional.pdf)

Ruta directa:

```text
docs/documentacion-tecnica-profesional.pdf
```

## Conclusión

Este laboratorio demuestra cómo un atacante puede levantar un servidor DHCP falso para entregar configuración de red maliciosa a una víctima. Al recibir como gateway y DNS la IP de Kali, la víctima queda bajo influencia del atacante, quien puede manipular la resolución de nombres y redirigir dominios hacia servicios falsos.

La mitigación aplicada, **DHCP Snooping**, bloquea respuestas DHCP provenientes de puertos no confiables. Esta medida evita que un servidor DHCP falso entregue configuración a los clientes y protege la red contra ataques de DHCP Spoofing.

## Autor

Este laboratorio fue realizado y documentado por:

**Michael David Robles Fermín**  
**iClexi**  
Matrícula: **2025-0845**

Repositorio del proyecto:

```text
https://github.com/iClexi/DHCP-Spoofing-Attack
```

Video demostrativo:

```text
https://www.youtube.com/watch?v=8mBYpaTNwKk
```
