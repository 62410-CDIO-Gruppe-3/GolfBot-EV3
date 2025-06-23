from __future__ import annotations

import socket
import threading
import queue
import time

from Movement.CommandLoop import collect_balls, move_to_goal


print_lock = threading.Lock()
EV3_IP = "192.168.82.36"   # ← IP address of your brick
PORT = 5532                  # Must match the server's port
TIMEOUT = 5.0               # Timeout in seconds for socket operations
MAX_RETRIES = 3             # Maximum number of connection retries

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

def collect_VIP_ball(    
    reference_point, 
    destination_point,
    robot_angle: float = 0.0, 
    iteration: int = 0
) -> None:
    command = collect_balls(    
        reference_point, 
        destination_point,
        robot_angle=robot_angle, 
        iteration=iteration
        )
    if command:
        print(f"Generated commands for collecting the VIP Ball (iteration {iteration+1}):")
        print(command)
        script = command
        response = send_and_receive(script)
        print("Response from EV3:", response)
        time.sleep(1)
    time.sleep(2)  
    return

def robot_move_to_goal(
    reference_point, 
    goal_point = None,
    robot_angle: float = 0.0,
    iteration: int = 8
) -> None:
    command = move_to_goal(
        reference_point, 
        goal_point,
        robot_angle=robot_angle,  
        iteration=iteration
    )
    if command:
        print(f"GOAL: Generated command for iteration: {iteration+1}" )
        print(command)
        script = command
        response = send_and_receive(script)
        print("Response from EV3:", response)
    return

def repeat_collection(
    reference_point, 
    destination_point,
    robot_angle: float = 0.0,
    inner_iteration: int = 6,
    outer_iteration: int = 5
) -> None:
    tip = reference_point
    for i in range(outer_iteration):
        for j in range(inner_iteration):
            command = collect_balls(
                tip,
                destination_point,
                robot_angle=robot_angle,
                iteration=j)
            if command:
                print(f"Generated command for iterations: (outer {i+1}, inner {j+1}):")
                print(command)
                script = command
                response = send_and_receive(script)
                print("Response from EV3:", response)
        print("AutonomousClient: Collecting ball at destination: ", destination_point)
    return
