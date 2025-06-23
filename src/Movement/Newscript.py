from __future__ import annotations

import socket
import threading
import queue
import time

EV3_IP = "172.20.10.4"   # Update with your EV3's IP address
PORT = 5532              # Must match the server's port
TIMEOUT = 5.0            # Timeout in seconds for socket operations
MAX_RETRIES = 3          # Number of connection retries

OPEN_GATE_CMD = "open_gate()\n"

def receive_response(sock, result_queue):
    """Receives data from EV3 and puts it in a queue."""
    try:
        data = []
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data.append(chunk)
        result_queue.put(b"".join(data).decode("utf-8"))
    except Exception as e:
        result_queue.put(f"Error receiving data: {e}")

def send_and_receive_command(command):
    """Sends a command to EV3 and returns the response."""
    for attempt in range(MAX_RETRIES):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            sock.connect((EV3_IP, PORT))
            sock.sendall(command.encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)

            result_queue = queue.Queue()
            thread = threading.Thread(target=receive_response, args=(sock, result_queue))
            thread.daemon = True
            thread.start()

            try:
                response = result_queue.get(timeout=TIMEOUT)
                return response
            except queue.Empty:
                if attempt == MAX_RETRIES - 1:
                    return "Timeout: No response from EV3"
                continue
        except socket.timeout:
            if attempt == MAX_RETRIES - 1:
                return "Connection to EV3 timed out"
            continue
        except ConnectionRefusedError:
            if attempt == MAX_RETRIES - 1:
                return "Connection was refused by EV3"
            time.sleep(0.5)
            continue
        except Exception as e:
            return f"Unexpected error: {e}"
        finally:
            try:
                sock.close()
            except Exception:
                pass

def main():
    print("Testing if the gate opens...")
    response = send_and_receive_command(OPEN_GATE_CMD)
    print("Response from EV3:", response)

if __name__ == "__main__":
    main()