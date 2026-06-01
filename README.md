# AGENTS.md

## Contexto del proyecto

Este repositorio pertenece a una práctica académica de Seguridad de Redes. El objetivo es documentar y demostrar un ataque DHCP Spoofing dentro de un laboratorio autorizado en GNS3.

## Autor

- Autor: Michael David Robles Fermín / iClexi
- Matrícula: 2025-0845
- Repositorio: https://github.com/iClexi/DHCP-Spoofing-Attack
- Video: https://www.youtube.com/watch?v=8mBYpaTNwKk

## Alcance autorizado

El contenido de este repositorio debe interpretarse únicamente como material educativo para laboratorio controlado. No está diseñado para redes públicas, empresariales o de terceros.

## Orden de revisión recomendado

1. Revisar la topología del laboratorio.
2. Revisar la configuración DHCP legítima en R-1.
3. Revisar la ejecución del script `dhcp-spoofing.py`.
4. Verificar que PC1 recibe gateway y DNS desde Kali.
5. Revisar el proceso DORA mostrado por el script.
6. Revisar la demostración de DNS y página falsa.
7. Revisar la mitigación con DHCP Snooping.
8. Verificar que PC1 no acepta DHCP del servidor falso después de la mitigación.

## Evidencias esperadas

Las capturas están en la carpeta `images/` y la documentación técnica profesional está en `docs/`.
