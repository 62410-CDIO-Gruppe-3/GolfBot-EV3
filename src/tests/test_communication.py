"""
tests/test_communication.py – Test af kommunikation mellem PC og EV3
Tester at koordinater kan sendes og modtages via communication.py
"""

import threading
import time
from communication import send_coordinates_to_ev3, receive_command_from_pc

def run_receiver():
    print("Starter receiver (EV3-side)...")
    data = receive_command_from_pc()
    print(f"Modtaget data: {data}")

def run_sender():
    print("Sender koordinater (PC-side)...")
    test_coords = [(100, 200), (300, 400), (500, 600)]
    time.sleep(1)  # Giv receiver tid til at starte op
    send_coordinates_to_ev3(test_coords)
    print("Koordinater sendt.")

if __name__ == "__main__":
    # Kør både sender og receiver i samme script for test (normalt kører de på hver sin enhed)
    receiver_thread = threading.Thread(target=run_receiver)
    sender_thread = threading.Thread(target=run_sender)

    receiver_thread.start()
    sender_thread.start()

    receiver_thread.join()
    sender_thread.join()
    print("Kommunikationstest afsluttet.")