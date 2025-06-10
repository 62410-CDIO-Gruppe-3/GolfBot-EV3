#!/usr/bin/env python3
"""PC-side client for GolfBot (updated to match the 2025 EV3 server API).

Keys (case-insensitive):
    W – drive forward
    S – turn right
    A – turn left
    V – open gate
    C – close gate
    P – push out (ball)
    R – push return (retract pusher)
    X – *immediate* stop of drive base
    Q – quit the program

Adjust ``EV3_IP`` as needed for your network.
"""

from __future__ import annotations

import socket
import threading
import queue
import time

print_lock = threading.Lock()
EV3_IP = "192.168.199.36"   # ← IP address of your brick
PORT = 5532                  # Must match the server's port
TIMEOUT = 5.0               # Timeout in seconds for socket operations
MAX_RETRIES = 3             # Maximum number of connection retries

HELLO_SCRIPT = 'print("Hello from PC Client")\n'

# --- movement parameters ----------------------------------------------
FORWARD_MM = 500    # positive = forward (edit to suit)
TURN_DEG   = 45     # degrees to turn with A/S keys

# ----------------------------------------------------------------------
# Networking helper
# ----------------------------------------------------------------------

def receive_data(sock: socket.socket, result_queue: queue.Queue) -> None:
    """Receive data from socket and put it in the result queue."""
    try:
        chunks: list[bytes] = []
        while chunk := sock.recv(1024):
            chunks.append(chunk)
        result_queue.put(b"".join(chunks).decode("utf-8"))
    except Exception as e:
        result_queue.put(f"Error receiving data: {str(e)}")

def create_socket() -> socket.socket:
    """Create and configure a new socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    return sock

def send_and_receive(script: str) -> str:
    """Send *script* to the EV3 and return its textual reply."""
    for attempt in range(MAX_RETRIES):
        try:
            sock = create_socket()
            sock.connect((EV3_IP, PORT))
            sock.sendall(script.encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)

            result_queue = queue.Queue()
            receive_thread = threading.Thread(target=receive_data, args=(sock, result_queue))
            receive_thread.daemon = True
            receive_thread.start()

            # Wait for response with timeout
            try:
                response = result_queue.get(timeout=TIMEOUT)
                sock.close()
                return response
            except queue.Empty:
                sock.close()
                if attempt == MAX_RETRIES - 1:
                    return "Timeout waiting for response from EV3"
                continue
        except socket.timeout:
            if attempt == MAX_RETRIES - 1:
                return "Connection timeout"
            continue
        except ConnectionRefusedError:
            if attempt == MAX_RETRIES - 1:
                return "Connection refused by EV3"
            time.sleep(0.5)  # Wait before retrying
            continue
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            try:
                sock.close()
            except:
                pass

# ----------------------------------------------------------------------
# Key → command mapper
# ----------------------------------------------------------------------

def build_command(key: str) -> str:
    k = key.lower()
    if k == "w":
        return f"drive_straight_mm({FORWARD_MM})\n"
    if k == "d":
        return f"turn_right_deg({TURN_DEG})\n"
    if k == "a":
        return f"turn_left_deg({TURN_DEG})\n"
    if k == "v":
        return "open_gate()\n"
    if k == "c":
        return "close_gate()\n"
    if k == "p":
        return "push_out()\n"
    if k == "r":
        return "push_return()\n"
    if k == "x":
        return "golfbot.stop()\n"
    # default: say hello so we always send *something*
    return HELLO_SCRIPT

# ----------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------

def main() -> None:
    print(
        "Press keys:\n"
        "  W – forward   D – right   A – left\n"
        "  V – open gate C – close gate\n"
        "  P – push out  R – push return\n"
        "  X – STOP      Q – quit\n"
    )
    while True:
        key = input("> ").strip()
        if key.lower() == "q":
            break
        script = build_command(key)
        reply = send_and_receive(script)
        print("EV3:", reply)


if __name__ == "__main__":
    main()