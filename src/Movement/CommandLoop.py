import math

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

    if reference_point is None or destination_point is None:
        return None
    
    vector = ArrowVector(reference_point, destination_point)
    distance = vector.get_size()
    ball_angle = vector.get_angle()
    
    if ball_angle < robot_angle:
        angle = robot_angle - math.abs(ball_angle)
    else:
        angle = robot_angle - ball_angle

    print(f"Tip of the robot: {reference_point},\n Destination: {destination_point}")

    print(f"Distance: {distance},\n Ball Angle: {ball_angle},\n Robot Angle: {robot_angle}")

    match iteration:
        case 0:
            if 0 < angle < 180.0:
                    input = f"turn_left_deg({angle})\n"
            else:
                    input = f"turn_right_deg({math.abs(angle)})\n"
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

    if reference_point is None or goal_point is None:
        return None

    vector = ArrowVector(reference_point, goal_point)
    distance = vector.get_size()
    goal_angle = vector.get_angle()
    
    if goal_angle < robot_angle:
        angle = robot_angle - math.abs(goal_angle)
    else:
        angle = goal_angle - robot_angle

    print(f"Tip of the robot: {reference_point},\n Goal: {goal_point}")
     
    print(f"Distance: {distance},\n Goal Angle: {goal_angle},\n Robot Angle: {robot_angle}")

    match iteration:
        case 0:
            if 0 < angle < 180.0:
                    input = f"turn_left_deg({angle})\n"
            else:
                    input = f"turn_right_deg({angle})\n"
        case 1:
                input = f"drive_straight_mm({150})\n"
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