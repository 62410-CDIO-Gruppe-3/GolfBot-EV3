import math
import time

from PathFinding.PointsGenerator import get_closest_path_point
from PathFinding.ArrowVector import ArrowVector


def collect_balls(reference_point, destination_point, robot_angle, iteration: int = 0):
    """
    Create an input dictionary for the pathfinding algorithm.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        dict: Input dictionary containing transformed points and arrow vectors.
    """
    print("Moving to collect balls...")

    if reference_point is None or destination_point is None:
        return None
    
    vector = ArrowVector(reference_point, destination_point)
    distance = vector.get_size()
    ball_angle = vector.get_angle()
    angle = 0

    print(f"robot_angle: {robot_angle}, ball_angle: {ball_angle}")
    
    if robot_angle <= 0 and ball_angle <= 0 and abs(robot_angle) <= abs(ball_angle):
        angle = (abs(ball_angle) - abs(robot_angle))* -1
        print(f"Angle: {angle} = Robot Angle: {robot_angle} - Ball Angle: {ball_angle}")
    elif robot_angle <= 0 and ball_angle <= 0 and abs(robot_angle) >= abs(ball_angle):
        angle = abs(robot_angle) - abs(ball_angle)
        print(f"Angle: {angle} = Robot Angle: {robot_angle} - Ball Angle: {ball_angle}")
    elif -90 < robot_angle < 0 and 0 < ball_angle <= 90:
        angle = abs(robot_angle) + ball_angle
        print(f"Angle: {angle} = Robot Angle: {robot_angle} + Ball Angle: {ball_angle}")
    elif robot_angle < 0 and 90 < ball_angle < 180:
        angle = ((180 - abs(robot_angle)) + (180 - ball_angle))*-1
        print(f"Angle: {angle} = (180 - Robot Angle: {robot_angle}) + (180 - Ball Angle: {ball_angle}) * -1")
    elif 0 < robot_angle and 0 < ball_angle and abs(robot_angle) <= abs(ball_angle):
        angle = abs(ball_angle) - abs(robot_angle)
        print(f"Angle: {angle} = Ball Angle: {ball_angle} - Robot Angle: {robot_angle}")
    elif 0 < robot_angle and 0 < ball_angle and abs(robot_angle) >= abs(ball_angle):
        angle = (abs(robot_angle) - abs(ball_angle))* -1
        print(f"Angle: {angle} = Robot Angle: {robot_angle} - Ball Angle: {ball_angle}")
    elif 0 < robot_angle < 90 and ball_angle < 0:
        angle = (abs(robot_angle) + 180 - abs(ball_angle)) * -1
        print(f"Angle: {angle} =  (Robot Angle: {robot_angle} + 180 - Ball Angle: {ball_angle}) * -1")
    elif 90 < robot_angle < 180 and ball_angle < 0:
        angle = (180 - abs(robot_angle)) + (180 - abs(ball_angle))
        print(f"Angle: {angle} = (180 - Robot Angle: {robot_angle}) + (180 - Ball Angle: {ball_angle})")
        
    print(f"Tip of the robot: {reference_point}")
    time.sleep(1)
    print(f"Destination: {destination_point}")
    time.sleep(1)
    print(f"Robot angle: {robot_angle}")
    time.sleep(1)
    print(f"Ball angle: {ball_angle}")
    time.sleep(1)
    #print(f"Angle: {angle}")
    #time.sleep(1)


    print(f"Distance: {distance},\n Ball Angle: {ball_angle},\n Robot Angle: {robot_angle}")

    match iteration:
        case 0:
            if 0 < angle < 180.0:
                    input = f"turn_right_deg({angle})\n"
            else:
                    input = f"turn_left_deg({abs(angle)})\n"
        case 1:
                input = f"drive_straight_mm({distance - 50})\n"
        case 2:  
                input = f"open_gate()\n"
        case 3:
                input = f"drive_straight_mm({50})\n"
        case 4:
                input = f"stop_drive()\n"
        case 5:
                input = f"close_gate()\n"
    return input

def move_to_goal(reference_point, goal_point, robot_angle, iteration: int = 0):
    """
    Create an input dictionary for the pathfinding algorithm to move to the goal.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        dict: Input dictionary containing transformed points and arrow vectors.
    """

    print("Moving to goal...")

    if reference_point is None or goal_point is None:
        return None

    vector = ArrowVector(reference_point, goal_point)
    distance = vector.get_size()
    goal_angle = vector.get_angle()
    
    if abs(goal_angle) < abs(robot_angle):
        angle = abs(robot_angle) - abs(goal_angle)
    else:
        angle = goal_angle - robot_angle

    print(f"Tip of the robot: {reference_point}")
    time.sleep(1)
    print(f"Destination: {goal_point}")
    time.sleep(1)
    print(f"Robot angle: {robot_angle}")
    time.sleep(1)
    print(f"Goal angle: {goal_angle}")
    time.sleep(1)
    print(f"Angle: {angle}")
    time.sleep(1)

    match iteration:
        case 0:
            if 0 < angle < 180.0:
                    input = f"turn_right_deg({angle})\n"
            else:
                    input = f"turn_left_deg({abs(angle)})\n"
        case 1:
                input = f"drive_straight_mm({distance - 50})\n"
        case 2:
                input = f"stop_drive()\n"
        case 3:
                input = f"open_gate()\n"
        case 4:
                input = f"push_out()\n"
        case 5:
                input = f"push_return()\n"
        case 6:
                input = f"drive_straight_mm({-50})\n"
        case 7:
                input = f"close_gate()\n"   
    return input