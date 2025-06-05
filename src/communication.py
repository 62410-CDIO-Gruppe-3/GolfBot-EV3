"""
communication.py – Simpel kommunikation mellem PC og EV3
Bruger TCP/IP sockets til at sende og modtage koordinater og kommandoer.
"""

import socket
import json

# Konfiguration
EV3_IP = "192.168.0.10"  # Sæt EV3'ens IP-adresse her
EV3_PORT = 9999

def send_coordinates_to_ev3(coordinates, host=EV3_IP, port=EV3_PORT):
    """
    Sender koordinater (liste af dicts eller tuples) til EV3 via TCP/IP.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        data = json.dumps({"coordinates": coordinates})
        s.sendall(data.encode("utf-8"))

def receive_command_from_pc(host="", port=EV3_PORT):
    """
    Lytter på porten og modtager kommandoer fra PC.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024)
            if data:
                return json.loads(data.decode("utf-8"))
    return None

# Eksempel på brug:
if __name__ == "__main__":
    # På PC: send_coordinates_to_ev3([(100, 200), (300, 400)])
    # På EV3: cmd = receive_command_from_pc()
    pass