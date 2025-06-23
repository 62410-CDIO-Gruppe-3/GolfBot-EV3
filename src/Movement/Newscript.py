from __future__ import annotations

import socket
import threading
import queue
import time

#from PathFinding.PointsGenerator import get_closest_path_point

#from Movement.CommandLoop import collect_balls, move_to_goal


print_lock = threading.Lock()
EV3_IP = "172.20.10.4"   # ← IP address of your brick
PORT = 5532                  # Must match the server's port
TIMEOUT = 5.0               # Timeout in seconds for socket operations
MAX_RETRIES = 3             # Maximum number of connection retries

# Constants for robot movement

ANGLE = 360
DISTANCE = 100

# ----------------------------------------------------------------------

OPEN_GATE = f"open_gate()\n"
CLOSE_GATE = f"close_gate()\n"
PUSH_GATE = f"push_out()\n"
PUSH_RETURN = f"push_return()\n"
MOVE_FORWARD = f"drive_straight_mm({DISTANCE})\n"
MOVE_BACKWARD = f"drive_straight_mm({-DISTANCE})\n"
CLOCKWISE_REVOLUTION = f"turn_left_deg({ANGLE})\n"
COUNTERCLOCKWISE_REVOLUTION = f"turn_right_deg({ANGLE+4})\n"

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

#def turnAndGo()

def main() -> None:
    print("Sending commands to EV3...")
    # Substitute commands you want to test in the brackets below
    response = send_and_receive("print('Hello from EV3')\n")
    print("Response from EV3:", response)
    time.sleep(1)
    response = send_and_receive(CLOCKWISE_REVOLUTION)
    print("Response from EV3:", response)
    time.sleep(5)
    response = send_and_receive(COUNTERCLOCKWISE_REVOLUTION)
    print("Response from EV3:", response)
    time.sleep(1)
    response = send_and_receive(OPEN_GATE)
    print("Response from EV3:", response)
    time.sleep(1)
    response = send_and_receive(OPEN_GATE)
    print("Response from EV3:", response)
    #time.sleep(1)
    response = send_and_receive(PUSH_GATE)
    print("Response from EV3:", response)
    #time.sleep(1)
    response = send_and_receive(PUSH_RETURN)
    print("Response from EV3:", response)
    time.sleep(1)
    response = send_and_receive(CLOSE_GATE)
    print("Response from EV3:", response)
"""
response = send_and_receive(CLOCKWISE_REVOLUTION)
print("Response from EV3:", response)
time.sleep(1)

response = send_and_receive(COUNTERCLOCKWISE_REVOLUTION)
print("Response from EV3:", response)
time.sleep(1)
"""
if __name__ == "__main__":
    main()
