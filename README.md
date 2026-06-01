# Ataque DHCP Spoofing

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-red)
![Environment](https://img.shields.io/badge/Environment-GNS3%20%7C%20IOSvL2-orange)
![Use](https://img.shields.io/badge/Use-Controlled%20Lab-yellow)
![Topic](https://img.shields.io/badge/Topic-Network%20Security-purple)

## Información del proyecto

Este repositorio documenta y demuestra un ataque **DHCP Spoofing** dentro de un laboratorio controlado de Seguridad de Redes. El ataque consiste en levantar un servidor DHCP no autorizado desde Kali Linux para entregar a la víctima una configuración de red manipulada, incluyendo gateway y DNS apuntando hacia el atacante.

**Autor:** Michael David Robles Fermín / iClexi  
**Matrícula:** 2025-0845  
**Repositorio:** https://github.com/iClexi/DHCP-Spoofing-Attack  
**Video demostrativo:** https://www.youtube.com/watch?v=8mBYpaTNwKk

## Documentación técnica profesional

Para una explicación más formal y detallada del ataque, la topología, el funcionamiento del script, las evidencias y las contramedidas aplicadas, consultar el siguiente documento:

[Ver documentación técnica profesional](docs/documentacion-tecnica-profesional.pdf)

Ruta directa del archivo: `docs/documentacion-tecnica-profesional.pdf`

## Aviso de uso responsable

Este proyecto fue desarrollado únicamente con fines educativos, académicos y de laboratorio controlado. Los scripts y comandos deben ejecutarse solamente en entornos propios o autorizados, como GNS3, EVE-NG, PNETLab o laboratorios internos de práctica.

No debe utilizarse en redes públicas, empresariales o de terceros sin autorización explícita.

## Objetivo del laboratorio

Demostrar cómo un atacante conectado a la misma red local puede ejecutar un servidor DHCP falso para entregar parámetros de red maliciosos a una víctima. El laboratorio evidencia cómo la víctima puede aceptar como gateway y DNS al equipo atacante, permitiendo manipulación de tráfico y resolución de dominios hacia servicios falsos.

## Topología utilizada

![Topología del laboratorio](images/01_topologia.png)

| Dispositivo | Interfaz | Dirección IP | Rol |
|---|---|---|---|
| R-1 | FastEthernet0/0 | `20.25.8.45/24` | Gateway y DHCP legítimo |
| SW-1 | Gi0/0 | N/A | Conexión hacia R-1 |
| SW-1 | Gi0/1 | N/A | Conexión hacia Kali |
| SW-1 | Gi0/2 | N/A | Conexión hacia PC1 |
| Kali Linux | eth0 | `20.25.8.46/24` | Atacante, DHCP/DNS/Web falso |
| PC1/VPCS | e0 | DHCP | Víctima |

## Procedimiento resumido

### 1. Configuración básica de DHCP en R-1

El router R-1 funciona como servidor DHCP legítimo antes del ataque. Esta configuración representa el estado normal del laboratorio.

![Configuración básica de DHCP en R-1](images/02_configuracion_dhcp_r1.png)

### 2. Ejecución del script DHCP Spoofing

Desde Kali Linux se ejecuta el script `dhcp-spoofing.py`, seleccionando la interfaz conectada al switch.

```bash
sudo python3 dhcp-spoofing.py
```

![Ejecución del script DHCP Spoofing](images/03_ejecucion_script.png)

### 3. DHCP exitoso en PC1 con servidor malicioso

PC1 recibe una dirección IP desde Kali y toma como gateway el equipo atacante `20.25.8.46`.

![PC1 obtiene configuración DHCP desde Kali](images/04_dhcp_exitoso_pc1.png)

### 4. Proceso DORA desde servidor malicioso

El script evidencia el proceso DHCP completo mediante mensajes `OFFER` y `ACK` enviados a los clientes.

![DORA desde servidor DHCP malicioso](images/05_dora_servidor_malicioso.png)

### 5. Página falsa aprovechando el DNS entregado por DHCP

Como PC1 recibió a Kali como DNS, el atacante puede resolver dominios hacia servicios falsos controlados por él.

![Servidor web falso en Kali](images/06_pagina_falsa.png)

### 6. Listener DNS falso

El script `fake-dns.py` responde consultas para dominios de laboratorio como `demo.local`.

![Listener DNS falso](images/07_listener_dns_falso.png)

### 7. Ping hacia demo.local

La víctima resuelve `demo.local` hacia `20.25.8.46`, demostrando el control DNS obtenido mediante DHCP Spoofing.

![Ping hacia demo.local](images/08_ping_demo_local.png)

### 8. Mitigación con DHCP Snooping

La contramedida aplicada es **DHCP Snooping**, configurando como confiable únicamente el puerto hacia R-1 y dejando como no confiables los puertos hacia Kali y PC1.

![Configuración de DHCP Snooping](images/09_dhcp_snooping_switch.png)

### 9. Verificación posterior a la mitigación

Después de aplicar DHCP Snooping, PC1 no recibe configuración del servidor DHCP falso, lo que evidencia que el switch bloquea las respuestas DHCP maliciosas.

![PC1 no encuentra servidor DHCP falso después de la mitigación](images/10_dhcp_bloqueado_post_mitigacion.png)

## Video demostrativo

La demostración práctica del ataque y su mitigación está disponible en YouTube:

[Ver video del laboratorio en YouTube](https://www.youtube.com/watch?v=8mBYpaTNwKk)

URL directa: https://www.youtube.com/watch?v=8mBYpaTNwKk

## Conclusión

Este laboratorio demuestra cómo un servidor DHCP no autorizado puede manipular la configuración de red de una víctima, entregando gateway y DNS controlados por el atacante. A partir de ese control, el atacante puede redirigir tráfico, manipular resolución de nombres y presentar servicios falsos dentro del laboratorio.

La mitigación más adecuada en switches Cisco es **DHCP Snooping**, configurando como confiable únicamente el puerto hacia el servidor DHCP legítimo y dejando como no confiables los puertos de usuario. De esta forma, el switch bloquea respuestas DHCP provenientes de Kali y evita que la víctima acepte configuraciones maliciosas.

## Autor

Este laboratorio fue realizado y documentado por:

**Michael David Robles Fermín / iClexi**  
Matrícula: **2025-0845**
