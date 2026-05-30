# Mitigación contra DHCP Spoofing

## Descripción

Esta mitigación se enfoca en proteger una red contra ataques **DHCP Spoofing**, donde un atacante levanta un servidor DHCP falso para entregar configuración de red maliciosa a una víctima.

En este laboratorio, Kali actúa como servidor DHCP falso y entrega parámetros como:

```text
IP asignada:       20.25.8.100
Gateway falso:     20.25.8.46
DNS falso:         20.25.8.46
DHCP Server falso: 20.25.8.46
```

El riesgo principal es que la víctima acepte una configuración de red controlada por el atacante, permitiendo redirección de tráfico, manipulación DNS o pérdida de conectividad.

---

## Contramedida principal

La contramedida principal contra DHCP Spoofing es:

```text
DHCP Snooping
```

DHCP Snooping permite al switch diferenciar entre puertos confiables y no confiables.

* Los puertos confiables pueden enviar respuestas DHCP.
* Los puertos no confiables no pueden enviar respuestas DHCP Offer ni DHCP ACK.

De esta forma, solo el servidor DHCP legítimo puede entregar configuración a los clientes.

---

## Topología de referencia

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
        |DHCP falso |              | Cliente   |
        +-----------+              +-----------+
```

---

## Direccionamiento del laboratorio

| Dispositivo | Rol                     |  Dirección IP | Descripción                       |
| ----------- | ----------------------- | ------------: | --------------------------------- |
| R1          | Gateway / DHCP legítimo | 20.25.8.45/24 | Servidor DHCP autorizado          |
| Kali        | Atacante / DHCP falso   | 20.25.8.46/24 | Servidor DHCP no autorizado       |
| VPC         | Víctima                 |          DHCP | Cliente que solicita dirección IP |
| SW-1        | Switch                  |           N/A | Switch Cisco IOSvL2               |

---

## Puertos de la topología

| Puerto | Conectado a        | Clasificación |
| ------ | ------------------ | ------------- |
| Gi0/0  | R1 / DHCP legítimo | Confiable     |
| Gi0/1  | Kali / DHCP falso  | No confiable  |
| Gi0/2  | VPC / Cliente DHCP | No confiable  |

---

## Variables que debes cambiar

Antes de aplicar la configuración, reemplaza los valores según tu topología.

| Variable                      | Significado                        | Ejemplo                  |
| ----------------------------- | ---------------------------------- | ------------------------ |
| `<VLAN_ID>`                   | VLAN donde se ejecuta DHCP         | `1`                      |
| `<TRUSTED_INTERFACE>`         | Puerto hacia el DHCP legítimo      | `gigabitEthernet0/0`     |
| `<UNTRUSTED_INTERFACE_RANGE>` | Puertos hacia clientes o atacantes | `gigabitEthernet0/1 - 2` |

---

## Nota sobre la VLAN

Si no configuraste una VLAN personalizada, normalmente los puertos están en la VLAN por defecto:

```text
VLAN 1
```

En ese caso, usa:

```text
<VLAN_ID> = 1
```

Si tu laboratorio usa otra VLAN, reemplaza `1` por la VLAN correspondiente.

---

## Configuración genérica

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan <VLAN_ID>
no ip dhcp snooping information option

interface <TRUSTED_INTERFACE>
description Puerto_confiable_hacia_DHCP_legitimo
ip dhcp snooping trust

interface range <UNTRUSTED_INTERFACE_RANGE>
description Puertos_no_confiables_clientes_o_atacantes
no ip dhcp snooping trust

end
write memory
```

---

## Configuración aplicada al laboratorio

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

## Explicación de la configuración

### 1. Activar DHCP Snooping globalmente

```cisco
ip dhcp snooping
```

Este comando activa la función DHCP Snooping en el switch.

---

### 2. Activar DHCP Snooping en la VLAN

```cisco
ip dhcp snooping vlan 1
```

Este comando indica en qué VLAN se aplicará la protección.

En este laboratorio se usa VLAN 1 porque no se configuró una VLAN personalizada.

---

### 3. Deshabilitar Option 82

```cisco
no ip dhcp snooping information option
```

En algunos laboratorios virtuales, la inserción de Option 82 puede causar problemas con servidores DHCP simples o routers básicos. Por eso se deshabilita para mantener compatibilidad.

---

### 4. Marcar como confiable el puerto hacia R1

```cisco
interface gigabitEthernet0/0
ip dhcp snooping trust
```

Este puerto conecta al servidor DHCP legítimo. Por eso se marca como confiable.

Desde este puerto se permiten mensajes DHCP como:

```text
DHCP Offer
DHCP ACK
DHCP NAK
```

---

### 5. Mantener como no confiable el puerto hacia Kali

```cisco
interface gigabitEthernet0/1
no ip dhcp snooping trust
```

Este puerto conecta al atacante. Como no es confiable, el switch bloquea respuestas DHCP enviadas desde Kali.

Esto evita que la víctima acepte configuración como:

```text
Gateway: 20.25.8.46
DNS:     20.25.8.46
```

---

### 6. Mantener como no confiable el puerto hacia la VPC

```cisco
interface gigabitEthernet0/2
no ip dhcp snooping trust
```

La VPC es un cliente DHCP. Los clientes pueden enviar solicitudes DHCP, pero no deben enviar respuestas DHCP.

---

## Verificación de DHCP Snooping

Después de aplicar la configuración, usa:

```cisco
show ip dhcp snooping
```

Resultado esperado:

```text
DHCP snooping is enabled
DHCP snooping is configured on VLAN 1
Interface Gi0/0 is trusted
Interface Gi0/1 is untrusted
Interface Gi0/2 is untrusted
```

También puedes verificar la tabla de bindings:

```cisco
show ip dhcp snooping binding
```

Esta tabla debe mostrar las asignaciones DHCP legítimas aprendidas por el switch.

---

## Prueba antes de la mitigación

Antes de aplicar DHCP Snooping, Kali puede responder a la víctima con DHCP falso.

En Kali:

```text
OFFER enviado -> cliente=00:50:79:66:68:00 ip=20.25.8.100 gateway=20.25.8.46 dns=20.25.8.46
ACK enviado -> cliente=00:50:79:66:68:00 ip=20.25.8.100 gateway=20.25.8.46 dns=20.25.8.46
```

En la VPC:

```text
IP/MASK     : 20.25.8.100/24
GATEWAY     : 20.25.8.46
DNS         : 20.25.8.46
DHCP SERVER : 20.25.8.46
```

Esto demuestra que el ataque DHCP Spoofing fue exitoso.

---

## Prueba después de la mitigación

Con el servidor DHCP falso todavía corriendo en Kali, renovar DHCP en la VPC:

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

La víctima debe recibir configuración únicamente del DHCP legítimo en R1.

---

## Evidencia esperada en el switch

Después de aplicar DHCP Snooping, el switch debe bloquear las respuestas DHCP falsas provenientes de Kali.

Comandos útiles:

```cisco
show ip dhcp snooping
show ip dhcp snooping binding
show logging | include DHCP|SNOOP|DHCPSNOOP
```

El resultado esperado es que:

* Gi0/0 aparezca como puerto confiable.
* Gi0/1 y Gi0/2 aparezcan como puertos no confiables.
* La VPC reciba DHCP desde R1.
* Kali no pueda entregar DHCP Offer ni DHCP ACK a la víctima.

---

## Mitigación complementaria: limitar tasa DHCP en puertos no confiables

Aunque el objetivo principal aquí es DHCP Spoofing, se puede agregar un límite de tasa para reducir abusos desde puertos no confiables.

```cisco
enable
configure terminal

interface range gigabitEthernet0/1 - 2
ip dhcp snooping limit rate 10

end
write memory
```

Este control limita la cantidad de mensajes DHCP permitidos por segundo en puertos no confiables.

Nota: esta medida es especialmente útil contra DHCP Starvation, pero también fortalece la defensa general de DHCP.

---

## Configuración completa recomendada

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
ip dhcp snooping limit rate 10

interface gigabitEthernet0/2
description Puerto_no_confiable_hacia_VPC_cliente
no ip dhcp snooping trust
ip dhcp snooping limit rate 10

end
write memory
```

---

## Reversión de la configuración

Si necesitas quitar la mitigación para repetir el ataque:

```cisco
enable
configure terminal

no ip dhcp snooping vlan 1
no ip dhcp snooping

interface gigabitEthernet0/0
no ip dhcp snooping trust

interface gigabitEthernet0/1
no ip dhcp snooping limit rate 10

interface gigabitEthernet0/2
no ip dhcp snooping limit rate 10

end
write memory
```

---

## Flujo recomendado para el video

1. Mostrar que la VPC recibe DHCP legítimo desde R1.
2. Ejecutar el servidor DHCP falso en Kali.
3. Renovar DHCP en la VPC.
4. Mostrar que la VPC recibió gateway, DNS y DHCP server desde Kali.
5. Mostrar la demo DNS maliciosa de laboratorio.
6. Aplicar DHCP Snooping en el switch.
7. Renovar DHCP nuevamente en la VPC.
8. Mostrar que ahora la VPC recibe DHCP desde R1.
9. Verificar DHCP Snooping con `show ip dhcp snooping`.
10. Concluir que el switch bloquea servidores DHCP no autorizados en puertos no confiables.

---

## Resultado esperado final

Después de la mitigación:

* Kali puede seguir conectado a la red, pero no puede actuar como servidor DHCP válido.
* Las respuestas DHCP desde Gi0/1 son bloqueadas.
* La VPC recibe configuración únicamente desde R1.
* La víctima ya no recibe gateway ni DNS falsos.
* El DNS falso deja de tener impacto porque la víctima ya no usa a Kali como servidor DNS.

---

## Recomendación final

La mejor práctica contra DHCP Spoofing es habilitar **DHCP Snooping** en el switch.

Solo los puertos hacia servidores DHCP legítimos deben marcarse como confiables. Todos los puertos de usuario, clientes, laboratorios o dispositivos no administrados deben permanecer como no confiables.

En esta práctica:

```text
Gi0/0 hacia R1  -> trusted
Gi0/1 hacia Kali -> untrusted
Gi0/2 hacia VPC  -> untrusted
```

Con esta configuración, el switch impide que Kali entregue ofertas DHCP falsas a la víctima.
