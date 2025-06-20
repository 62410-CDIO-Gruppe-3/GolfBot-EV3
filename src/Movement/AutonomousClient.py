from __future__ import annotations

import socket
import threading
import queue
import time


from ImageRecognition.Homography import create_homography, save_homography
from ImageRecognition.ImagePoints import get_transformed_points_from_image

import ImageRecognition.ArrowDetection as arrow_det

from PathFinding.PointsGenerator import get_closest_path_point

from Movement.CommandLoop import collect_balls, move_to_goal


print_lock = threading.Lock()
EV3_IP = "192.168.147.36"   # ← IP address of your brick
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
    iterations: int = 6
) -> None:
    for i in range(iterations):
        command = collect_balls(    
            reference_point, 
            destination_point,
            robot_angle=robot_angle, 
            iteration=i
        )
        if command:
            print(f"Generated commands for collecting the VIP Ball (iteration {i+1}):")
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
    iterations: int = 8
) -> None:
    for i in range(iterations):
        command = move_to_goal(
            reference_point, 
            goal_point,
            robot_angle=robot_angle,  
            iteration=i
        )
        if command:
            print(f"GOAL: Generated command for iteration: {i+1}" )
            print(command)
            script = command
            response = send_and_receive(script)
            print("Response from EV3:", response)
        time.sleep(1)
    time.sleep(2)
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
        time.sleep(1)
    time.sleep(2)  
    return


def main():
    reference_point = (0, 0)  # This should be the detected arrow tip
    robot_angle = 0.0  # This should be the robot's current angle
    goal_point = (100, 200) 
    tip = reference_point
    destination_points = [(100.01, 200.01), (150.01, 250.01), (200.01, 300.01), (600.01, 200.01), (300.01, 400.01), (1000.01, 800.01), 
                          (700.01, 700.01), (200.01,300.01), (400.01, 200.01), (800.01, 1200.01), (1500.01, 300.01)]  # Example points

    tip = reference_point
    closest_point = get_closest_path_point(destination_points, tip)

    # Collect VIP ball
    collect_VIP_ball(
        tip,
        destination_points,
        robot_angle=robot_angle,
        iterations=6
    )

    next_tip = closest_point 
    tip = next_tip 
    destination_points.remove(closest_point)

    time.sleep(2)  # Wait for a second before next action
    print("Updated tip for next actions:", tip)
    time.sleep(2)

    print("AutonomousClient: Updated list of destinations: ", destination_points, 
          "\n Length of destination points: ", len(destination_points),
            "\n Former closest point:", next_tip)
    
    time.sleep(2)  # Wait for a second before next action

    # Move to goal
    robot_move_to_goal(
        tip,
        goal_point=goal_point,
        robot_angle=robot_angle,
        iterations=8
    )

    next_tip = goal_point
    tip = next_tip
    print("Next tip (goal point):", next_tip)

    time.sleep(2)
    
    # Collect regular balls
    repeat_collection(
        tip, 
        destination_points,
        robot_angle=robot_angle, 
        inner_iteration=6, 
        outer_iteration=5
    )    

    # Move to goal again
    robot_move_to_goal(
        tip,
        goal_point=goal_point,
        robot_angle=robot_angle,
        iterations=8
    )

    next_tip = goal_point
    tip = next_tip
    print("Next tip (goal point):", next_tip)

    time.sleep(2)

    # Collect regular balls again
    repeat_collection(
        tip, 
        destination_points,
        robot_angle=robot_angle, 
        inner_iteration=6, 
        outer_iteration=5
    )

    time.sleep(2)     
    
    # Move to goal again
    robot_move_to_goal(
        tip,
        goal_point=goal_point,
        robot_angle=robot_angle,
        iterations=8
    )

    next_tip = goal_point
    tip = next_tip
    print("Next tip (goal point):", next_tip)

    time.sleep(2)
    exit (0)  # Exit the program
    
if __name__ == "__main__":
    main()