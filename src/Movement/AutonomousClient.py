from __future__ import annotations

import socket
import threading
import queue
import time

import os 
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ImageRecognition.Homography import create_homography, save_homography
from ImageRecognition.ImagePoints import get_transformed_points_from_image

import ImageRecognition.ArrowDetection as arrow_det

from PathFinding.PointsGenerator import get_closest_path_point

from CommandLoop import collect_balls, move_to_goal


print_lock = threading.Lock()
EV3_IP = "192.168.147.36"   # ← IP address of your brick
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

def build_commands_from_points( 
    reference_point, 
    destination_points, 
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
        commands = collect_balls(reference_point, destination_points)
    elif action == "move":
        if goal_point is None:
            raise ValueError("goal_point must be provided when action is 'move'")
        commands = move_to_goal(reference_point, goal_point)
    else:
        commands = ""
    return commands

def main():
    # Example usage
    reference_point = (0, 0)  # This should be the detected arrow tip
    tip = reference_point
    # transformed_points = get_transformed_points_from_image(image)
    destination_points = [(100.01, 200.01), (150.01, 250.01), (200.01, 300.01), (600.01, 200.01), (300.01, 400.01), (1000.01, 800.01), 
                          (700.01, 700.01), (200.01,300.01), (400.01, 200.01), (800.01, 1200.01), (1500.01, 300.01)]  # Example points
    script = HELLO_SCRIPT
    print("Sending script to EV3:\n", script)
    response = send_and_receive(script)

    # Collect balls
    commands = build_commands_from_points(tip, destination_points, action="collect")
    closest_point = get_closest_path_point(destination_points, tip)  # Get the closest point
    next_tip = closest_point  # Get the closest point
    tip = next_tip   # Update tip to the first transformed point for next actions
    print("Next tip (closest point):", next_tip)
    destination_points.remove(closest_point)  # Remove the closest point from the list

    print("AutonomousClient: Updated list of destinations: ", destination_points, 
          "\n Length of destination points: ", len(destination_points),
            "\n Former closest point:", closest_point)
    
    if commands:
        # print("Generated commands for collecting balls:")
        # print(commands)
        # response = send_and_receive(commands)
        # print("Response from EV3:", response)
        script = commands
    
    print("Sending commands to EV3:\n", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)
    


    # Move to goal
    goal_point = (100, 200)  # Example goal point

    commands = build_commands_from_points(tip, destination_points, action="move", goal_point=goal_point)
    if commands:
        # print("Generated commands for moving to goal:")
        # print(commands)
        # response = send_and_receive(commands)
        # print("Response from EV3:", response)
        script = commands
    
    print("Sending commands to EV3:\n", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)

    time.sleep(5)  # Wait for a second before next action

    next_tip = goal_point
    tip = next_tip
    print("Next tip (closest point):", tip, "Goal point:", goal_point)
    
    # Collect balls again
    for i in range(5):
        commands = build_commands_from_points(tip, destination_points, action="collect")
        closest_point = get_closest_path_point(destination_points, tip) # Get the closest point
        next_tip = closest_point  # Get the closest point
        print("Next tip (closest point):", next_tip)
        tip = next_tip  # Update tip to the first transformed point for next action
        destination_points.remove(closest_point)  # Remove the closest point from the lists
        print("Updated tip for next actions:", tip)
        print("AutonomousClient: Updated list of destinations: ", destination_points, 
          "\n Length of destination points: ", len(destination_points),
            "\n Former closest point:", closest_point)

        if commands:
            print(f"Generated commands for collecting balls (iteration {i+1}):")
            # print(commands)
            # response = send_and_receive(commands)
            # print("Response from EV3:", response)
            script = commands
        
        print("Sending commands to EV3:\n", script)
        response = send_and_receive(script)
        print("Response from EV3:", response)

    time.sleep(5)  # Wait for a second before next action        

    # Move to goal again
    commands = build_commands_from_points(tip, destination_points, action="move", goal_point=goal_point)
    if commands:
        print("Generated commands for moving to goal:")
        #print(commands)
        #response = send_and_receive(commands)
        #print("Response from EV3:", response)
        script = commands

    print("Sending commands to EV3:", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)

    next_tip = goal_point  # Update tip to goal point after moving
    tip = next_tip  # Update tip to goal point after moving
    print("Next tip (closest point):", tip, "Goal point:", goal_point)   

    time.sleep(5)  # Wait for a second before next action

    # Collect balls again
    for i in range(5):
        commands = build_commands_from_points(tip, destination_points, action="collect")
        closest_point = get_closest_path_point(destination_points, tip) # Get the closest point
        next_tip = closest_point  # Get the closest point
        print("Next tip (closest point):", next_tip)
        tip = next_tip  # Update tip to the first transformed point for next action
        destination_points.remove(closest_point)  # Remove the closest point from the lists
        print("Updated tip for next actions:", tip)
        print("AutonomousClient: Updated list of destinations: ", destination_points, 
          "\n Length of destination points: ", len(destination_points),
            "\n Former closest point:", closest_point)

        if commands:
            print(f"Generated commands for collecting balls (iteration {i+1}):")
            # print(commands)
            # response = send_and_receive(commands)
            # print("Response from EV3:", response)
            script = commands
        
        print("Sending commands to EV3:\n", script)
        response = send_and_receive(script)
        print("Response from EV3:", response)

    time.sleep(5)  # Wait for a second before next action        
    
    # Move to goal again
    commands = build_commands_from_points(tip, destination_points, action="move", goal_point=goal_point)
    if commands:
        print("Generated commands for moving to goal:")
        #print(commands)
        #response = send_and_receive(commands)
        #print("Response from EV3:", response)
        script = commands

    print("Sending commands to EV3:", script)
    response = send_and_receive(script)
    print("Response from EV3:", response)


if __name__ == "__main__":
    main()