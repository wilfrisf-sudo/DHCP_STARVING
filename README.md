# Laboratorio de Seguridad: Ataque DoS mediante DHCP Starvation

**Autor:** Wilfri Solano Frias  
**Matrícula:** 2024-2364   

-------------------------------------------------------------------------------------------------------------------------

## 1. Objetivo del Laboratorio
Conocer las vulnerabilidades y peligros reales de los conmutadores de red al procesar ráfagas masivas de solicitudes de control basadas en difusión (Broadcast). El escenario busca analizar cómo la falta de políticas de seguridad en los accesos permite inundar el conmutador, forzándolo a registrar miles de identidades falsas en su memoria CAM y a tramitar peticiones que vacían los recursos de direccionamiento de la LAN, provocando una denegación de servicio (DoS) para los hosts legítimos.

-------------------------------------------------------------------------------------------------------------------------

## 2. Objetivo del Script
Generar e inyectar de forma asíncrona un flujo masivo de tramas DHCP Discover utilizando direcciones MAC de origen aleatorias. Al mismo tiempo, el script utiliza hilos de fondo (Multithreading) para escuchar de forma activa el medio físico, interceptar las respuestas DHCP Offer provenientes del servidor legítimo y responder inmediatamente con un DHCP Request, consolidando el secuestro físico y lógico de las direcciones del segmento.

### 2.1. Requisitos para utilizar la herramienta
* **Sistema Operativo:** Kali Linux.
* **Lenguaje:** Python 3.x.
* **Librerías/Dependencias:** Scapy (módulos base de red) y la librería nativa `threading`. Instalar entorno de red con: `pip install scapy`.
* **Entorno de Red:** La interfaz del atacante debe estar conectada hacia un puerto del switch que pertenezca a la misma VLAN del servidor de asignación IP, en modo promiscuo y con privilegios de administrador (root).

### 2.2. Parámetros Usados
El script admite y manipula las siguientes variables y configuraciones:
* `INTERFACE = "eth0"`: Adaptador de red de la estación atacante enlazado al socket crudo de Scapy.
* `xid_mac_map = {}`: Diccionario dinámico en memoria RAM encargado de asociar cada ID de transacción aleatorio (`xid`) con su dirección física virtual correspondiente (`RandMAC()`) para contestar las ofertas del switch.
* `limite=300`: Número total de identidades ficticias y tramas DHCP de difusión inyectadas en la red durante la fase de estrés.
* `dst="ff:ff:ff:ff:ff:ff"` y `dst="255.255.255.255"`: Direcciones de Broadcast de Capa 2 y Capa 3 utilizadas para forzar al switch a replicar el paquete por todos sus puertos físicos.
* `message-type ("discover" / "request")`: Opciones del protocolo que definen la fase del ciclo de vida de la solicitud de direccionamiento de red.

-------------------------------------------------------------------------------------------------------------------------

## 3. Documentación del Funcionamiento del Script
El programa ejecuta un flujo paralelo mediante hilos de ejecución estructurados con la función `sendp()` y un analizador de fondo `sniff()`. El script arma en memoria tramas combinando la encapsulación UDP (`sport=68`, `dport=67`) exigida por el estándar y las cabeceras dinámicas BOOTP/DHCP mapeadas en un diccionario local.

Al inyectar estos paquetes por el puerto `Ethernet0/1`, el switch recibe notificaciones de difusión que afirman que existen cientos de clientes nuevos en la red. En un entorno desprotegido, el switch se ve obligado a registrar cada dirección física de origen en su tabla de conmutación (tabla CAM). Simultáneamente, el hilo de fondo intercepta los anuncios del servidor legítimo y dispara respuestas automáticas DHCP Request, forzando el desbordamiento total de la memoria física del switch y el vaciado del direccionamiento IP de la LAN en pocos segundos.

-------------------------------------------------------------------------------------------------------------------------


## 4. Documentación de la Red

### 4.1. Topología
* **Descripción:** Infraestructura simulada en GNS3 estructurada para evaluar la tolerancia del switch ante inundaciones por difusión y agotamiento de direccionamiento centralizado.
* **VLANs Configuradas:** VLAN 1 (Nativa / Por defecto).
* **Direccionamiento IP:**
  * **Segmento de Red:** `192.168.64.0` / `255.255.255.0`
  * **Atacante (Kali Linux):** Dirección MAC e IP generadas/gestionadas dinámicamente mediante el script de automatización.
* **Interfaces Clave:**
  * **Switch Principal Legítimo (SWI2):** Actúa originalmente como el switch extra para dar a notar cuál es el pool legítimo.
  * **Switch de Acceso bajo Prueba (SWI1):** Conmutador central bajo evaluación.
    * `Ethernet0/0`: Conectado hacia el switch SWI2.
    * `Ethernet0/1`: Conectado directamente a la estación atacante Kali Linux.

-------------------------------------------------------------------------------------------------------------------------

## 5. Contramedidas (Mitigación)

Para anular este vector de ataque y denegar la inyección de múltiples identidades ficticias en la infraestructura, se aplica la siguiente directiva de endurecimiento en el switch de acceso:

### 5.1 Implementación de Port Security con Acción de Apagado (Shutdown)
Consiste en forzar el puerto del usuario/atacante (`Ethernet0/1`) a modo acceso, limitar estrictamente la cantidad de direcciones MAC permitidas en la interfaz a una sola identidad física legítima y ordenar el apagado automático del puerto si el script intenta mutar las cabeceras de red.

SWI1# configure terminal
SWI1(config)# interface Ethernet0/1
SWI1(config-if)# switchport mode access
SWI1(config-if)# switchport port-security
SWI1(config-if)# switchport port-security maximum 1
SWI1(config-if)# switchport port-security violation shutdown
SWI1(config-if)# end
SWI1# write memory

-------------------------------------------------------------------------------------------------------------------------

## 6. Evidencias

### 6.1. Demostración en Video
En el siguiente enlace se encuentra el video demostrativo (máx. 5 minutos) donde se visualiza la topología con mi nombre y matrícula, la fecha y hora, la ejecución del ataque y la aplicación de la contramedida:  

https://www.youtube.com/watch?v=fhUzdaql5iI&list=PLGfNWxn7Di3BhsEEifmTJKXP4_U9fla7P&index=3

### 6.2. Capturas de Pantalla

#### A. Diseño de la Topología en GNS3

<img width="700" height="546" alt="imagen" src="https://github.com/user-attachments/assets/52bd48ae-1a54-4d97-b72c-be3938a440f9" />

#### B. Ejecución del Script

<img width="672" height="279" alt="imagen" src="https://github.com/user-attachments/assets/bf410163-24e6-4f31-96f5-535c1b49db4b" />

#### C. Agotamiento de Direcciones (Pool saturado)

<img width="643" height="403" alt="imagen" src="https://github.com/user-attachments/assets/a2724ea6-c96a-4442-9f29-47042a077c7b" />

#### D. Aplicación de Contramedidas

<img width="619" height="248" alt="imagen" src="https://github.com/user-attachments/assets/646251ae-73f3-4981-b112-d4160a65fa72" />

