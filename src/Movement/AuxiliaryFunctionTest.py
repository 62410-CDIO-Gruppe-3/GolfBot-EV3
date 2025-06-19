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

def command_sender(action: str = "collect",
                   iteration: int = 0,
                   angle: float = 0.0) -> None:
    
    if action == "collect":
       match iteration:
            case 0:
               if angle < 180.0:
                    input = f"turn_left_deg({angle})\n"
                    send_and_receive(input)
               else:
                    input = f"turn_right_deg({360 - angle})\n"
                    send_and_receive(input)
            case 1:
                input = f"drive_straight_mm({150})\n"
                send_and_receive(input)
            case 2:  
                input = f"open_gate()\n"
                send_and_receive(input)
            case 3:
                input = f"drive_straight_mm({50})\n"
                send_and_receive(input)
            case 4:
                input = f"stop_drive()\n"
                send_and_receive(input)
            case 5:
                input = f"close_gate()\n"
                send_and_receive(input)
            case 6:
                input = f"stop_all_motors()\n"
                send_and_receive(input)
            case 7:
                input = f"stop_all_motors()\n"
                send_and_receive(input)
    if action == "move_to_goal":
        match iteration:
            case 0:
                if angle < 180.0:
                    input = f"turn_left_deg({angle})\n"
                    send_and_receive(input)
                else:
                    input = f"turn_right_deg({360 - angle})\n"
                    send_and_receive(input)
            case 1:
                input = f"drive_straight_mm({150})\n"
                send_and_receive(input)
            case 2:
                input = f"stop_drive()\n"
                send_and_receive(input)
            case 3:
                input = f"open_gate()\n"
                send_and_receive(input)
            case 4:
                input = f"push_out()\n"
                send_and_receive(input)
            case 5:
                input = f"push_return()\n"
                send_and_receive(input)
            case 6:
                input = f"drive_straight_mm({-50})\n"
                send_and_receive(input)
            case 7:
                input = f"close_gate()\n"
                send_and_receive(input)        

def main() -> None:
    """
    Main function to run the command sender.
    """
    while True:
        for i in range(8):
            command_sender(action="collect", iteration=i, angle=45.0)
            time.sleep(1)
        for i in range(8):
            command_sender(action="move_to_goal", iteration=i, angle=225.0)
            time.sleep(1)

if __name__ == "__main__":
    main()
