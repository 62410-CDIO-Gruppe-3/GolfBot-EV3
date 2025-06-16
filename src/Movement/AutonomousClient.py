from __future__ import annotations

import socket
import threading
import queue
import time

import os 
import sys

sys.path.append("C:\\Users\\hatal\\GolfBot-EV3\\src")

from ImageRecognition.Homography import create_homography, save_homography
from ImageRecognition.ImagePoints import get_transformed_points_from_image

import ImageRecognition.ArrowDetection as arrow_det

from PathFinding.PointsGenerator import get_closest_path_points
from PathFinding.PathGenerator import get_arrow_vector_x, get_arrow_vector_y, get_arrow_vector_angle, get_arrow_vector_size

from CommandLoop import collect_balls, move_to_goal


print_lock = threading.Lock()
EV3_IP = "172.20.10.13"   # ← IP address of your brick
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

def build_commands_from_image(
    image, 
    reference_point, 
    transformed_points, 
    action: str = "collect", 
    goal_point = None
) -> str:
    """
    Generate movement commands from image recognition inputs.

    Args:
        image: The current image frame (BGR).
        arrow_template: Grayscale image of the arrow template.
        transformed_points: List or array of transformed points from the image.
        action: 'collect' to use collect_balls or 'move' to use move_to_goal.
        goal_point: Required if action is 'move'; specifies the target goal point.

    Returns:
        A string with the commands, or an empty string if generation fails.
    """
    if action == "collect":
        commands = collect_balls(image, reference_point, transformed_points)
    elif action == "move":
        if goal_point is None:
            raise ValueError("goal_point must be provided when action is 'move'")
        commands = move_to_goal(image, reference_point, goal_point)
    else:
        commands = ""
    return commands

def main():
    # Example usage
    image = "C:\\Users\\hatal\\GolfBot-EV3\\src\\assets\\test_image5.jpg"
    reference_point = (0, 0)  # This should be the detected arrow tip
    tip = reference_point
    transformed_points = get_transformed_points_from_image(image)
    script = HELLO_SCRIPT
    print("Sending script to EV3:", script)
    response = send_and_receive(script)

    # Collect balls
    commands = build_commands_from_image(image, tip, transformed_points, action="collect")
    if commands:
        print("Generated commands for collecting balls:")
        print(commands)
        response = send_and_receive(commands)
        print("Response from EV3:", response)
    
    script = commands
    print("Sending commands to EV3:", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)

    time.sleep(5)  # Wait for a second before next action

    # Move to goal
    goal_point = (100, 200)  # Example goal point
    commands = build_commands_from_image(image, tip, transformed_points, action="move", goal_point=goal_point)
    if commands:
        print("Generated commands for moving to goal:")
        print(commands)
        response = send_and_receive(commands)
        print("Response from EV3:", response)
    
    script = commands
    print("Sending commands to EV3:", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)

    time.sleep(5)  # Wait for a second before next action
    
    # Collect balls again
    for i in range(5):
        commands = build_commands_from_image(image, tip, transformed_points, action="collect")
        if commands:
            print(f"Generated commands for collecting balls (iteration {i+1}):")
            print(commands)
            response = send_and_receive(commands)
            print("Response from EV3:", response)
    
    script = commands
    print("Sending commands to EV3:", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)

    time.sleep(5)  # Wait for a second before next action        

    # Move to goal again
    commands = build_commands_from_image(image, tip, transformed_points, action="move", goal_point=goal_point)
    if commands:
        print("Generated commands for moving to goal:")
        print(commands)
        response = send_and_receive(commands)
        print("Response from EV3:", response)

    script = commands
    print("Sending commands to EV3:", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)   

    time.sleep(5)  # Wait for a second before next action

    # Collect balls again
    for i in range(5):
        commands = build_commands_from_image(image, tip, transformed_points, action="collect")
        if commands:
            print(f"Generated commands for collecting balls (iteration {i+1}):")
            print(commands)
            response = send_and_receive(commands)
            print("Response from EV3:", response)

    script = commands
    print("Sending commands to EV3:", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)

    time.sleep(5)  # Wait for a second before next action
    
    # Move to goal again
    commands = build_commands_from_image(image, tip, transformed_points, action="move", goal_point=goal_point)
    if commands:
        print("Generated commands for moving to goal:")
        print(commands)
        response = send_and_receive(commands)
        print("Response from EV3:", response)

    script = commands
    print("Sending commands to EV3:", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)    

if __name__ == "__main__":
    main()