import sys
sys.path.append(r"C:\\Users\\hatal\\GolfBot-EV3\\src")

import socket
EV3_IP = '192.168.43.36'    #ev3 ip
PORT = 5532                 #port thats being listened on

from ImageRecognition.ImagePoints import get_transformed_points_from_image
from ImageRecognition.ArrowDetection import detect_arrow_tip
from PathFinding.PointsGenerator import get_closest_path_points
from PathFinding.PathGenerator import get_arrow_vector_x, get_arrow_vector_y, get_arrow_vector_angle, get_arrow_vector_size

script1 = """
ev3.speaker.beep(20)
wait(200)
ev3.speaker.beep(100)
wait(200)
ev3.speaker.beep(200)
wait(200)
"""


image_path = r"assets\\image.jpg"

def SendRecieve(script):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((EV3_IP, PORT))
        client_socket.sendall(script.encode("utf-8"))        
        #done sending and ready to close connection
        client_socket.shutdown(socket.SHUT_WR)
        response = client_socket.recv(1024)
        return response.decode("utf-8")

def pick_up_ball():
    message = script1

    ReplyFromEV = SendRecieve(message)
    print("EV3: ", ReplyFromEV)

    
    # Get transformed points from the image
    transformed_points = get_transformed_points_from_image(image_path)
        
        # Detect the arrow tip
    arrow_tip = detect_arrow_tip(image_path)
    if arrow_tip is None:
        print("Arrow tip not detected.")
        return
        
    # Get the closest path points
    closest_point = get_closest_path_points(transformed_points, arrow_tip, num_points=1)
        
        # Calculate the arrow vector components
    dx = get_arrow_vector_x(image_path, arrow_tip, closest_point)
    dy = get_arrow_vector_y(image_path, arrow_tip, closest_point)
    angle = get_arrow_vector_angle(image_path, arrow_tip, closest_point)
    size = get_arrow_vector_size(image_path, arrow_tip, closest_point)

    if angle is None or size is None:
        print("Failed to calculate angle or size.")
        return

    if angle == 0:
        message = f"DriveStraightDist({-size})"
        
    if angle < 0:
        if dx < 0 or dy > 0:
            message = f"TurnLeft({abs(angle)})"
            message = f" DriveStraightDist({-size})"
        else:
            message = f"TurnRight({abs(angle)})"
            message = f" DriveStraightDist({-size})"

    message = f"OpenGate()"
    message = f"DriveStraightDist({-30})"
    message = f"CloseGate()"

def hand_in_balls():
    message = script1
    
    ReplyFromEV = SendRecieve(message)
    print("EV3: ", ReplyFromEV)
        
    # Detect the arrow tip
    arrow_tip = detect_arrow_tip(image_path)
    if arrow_tip is None:
        print("Arrow tip not detected.")
        return
        
    # Get the closest path points
    goal = (0, 0)
    
    goal_vector_dx = get_arrow_vector_x(image_path, arrow_tip, goal)  
    goal_vector_dy = get_arrow_vector_y(image_path, arrow_tip, goal)
    goal_vector_angle = get_arrow_vector_angle(image_path, arrow_tip, goal)
    goal_vector_size = get_arrow_vector_size(image_path, arrow_tip, goal)

    if goal_vector_angle is None or goal_vector_size is None:
        print("Failed to calculate goal vector angle or size.")
        return

    if goal_vector_angle == 0:
        message = f"DriveStraightDist({-goal_vector_size})"
        
    if goal_vector_angle < 0:
        if goal_vector_dx < 0 or goal_vector_dy > 0:
            message = f"TurnLeft({abs(goal_vector_angle)})"
            message = f" DriveStraightDist({-goal_vector_size})"
        else:
            message = f"TurnRight({abs(goal_vector_angle)})"
            message = f" DriveStraightDist({-goal_vector_size})"
        
    message = f"PushOut()"
    message = f"PushReturn()"

