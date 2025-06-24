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

    if -180 <= robot_angle <= -90 and -180 <= ball_angle <= -90 and abs(robot_angle) <= abs(ball_angle):
    # Both in Quadrant 4 (ball angle greater than robot angle)
        angle = ball_angle - robot_angle
    elif -180 <= robot_angle <= -90 and -180 <= ball_angle <= -90 and abs(robot_angle) >= abs(ball_angle):
    # Both in Quadrant 4 (robot angle greater than ball angle)
        angle = (abs(robot_angle) - abs(ball_angle)) * -1
    elif -180 <= robot_angle <= -90 and -90 < ball_angle <= 0:
    # Robot in Q4, Ball in Q3
        angle = (abs(robot_angle) + abs(ball_angle)) * -1
    elif -180 <= robot_angle <= -90 and 0 < ball_angle <= 90:
    # Robot in Q4, Ball in Q2
        angle = (180 - abs(robot_angle)) + ball_angle
    elif -180 <= robot_angle <= -90 and 90 < ball_angle <= 180:
    # Robot in Q4, Ball in Q1
        angle = (180 - abs(robot_angle)) + (180 - ball_angle)
        angle *= -1

    elif -90 < robot_angle <= 0 and -180 <= ball_angle <= -90:
    # Robot in Q3, Ball in Q4
        angle = ball_angle + robot_angle
    elif -90 < robot_angle <= 0 and -90 < ball_angle <= 0 and abs(robot_angle) <= abs(ball_angle):
    # Both in Q3 (ball angle greater than robot angle)
        angle = ball_angle - robot_angle
    elif -90 < robot_angle <= 0 and -90 < ball_angle <= 0 and abs(robot_angle) >= abs(ball_angle):
    # Both in Q3 (robot angle greater than ball angle)
        angle = (abs(robot_angle) - abs(ball_angle)) * -1
    elif -90 < robot_angle <= 0 and 0 < ball_angle <= 90:
    # Robot in Q3, Ball in Q2
        angle = abs(robot_angle) + ball_angle
    elif -90 < robot_angle <= 0 and 90 < ball_angle <= 180:
    # Robot in Q3, Ball in Q1
        angle = (180 + robot_angle) + (180 - ball_angle)
        angle *= -1

    elif 0 < robot_angle <= 90 and -180 <= ball_angle <= -90:
    # Robot in Q2, Ball in Q4
        angle = (180 - abs(ball_angle)) + robot_angle
    elif 0 < robot_angle <= 90 and -90 < ball_angle <= 0:
    # Robot in Q2, Ball in Q3
        angle = (robot_angle + abs(ball_angle)) - 1
    elif 0 < robot_angle <= 90 and 0 < ball_angle <= 90 and abs(robot_angle) <= abs(ball_angle):
    # Both in Q2  (ball angle greater than robot angle)
        angle = ball_angle - robot_angle
    elif 0 < robot_angle <= 90 and 0 < ball_angle <= 90 and abs(robot_angle) >= abs(ball_angle):
    # Both in Q2 (robot angle greater than ball angle)
        angle = (abs(robot_angle) - abs(ball_angle)) * -1
    elif 0 < robot_angle <= 90 and 90 < ball_angle <= 180:
    # Robot in Q2, Ball in Q1
        angle = (ball_angle - robot_angle)

    elif 90 < robot_angle <= 180 and -180 <= ball_angle <= -90:
    # Robot in Q1, Ball in Q4
        angle = (180 - abs(ball_angle)) + (180 - robot_angle)
    elif 90 < robot_angle <= 180 and -90 < ball_angle <= 0:
    # Robot in Q1, Ball in Q3
        angle = (180 + ball_angle) + (robot_angle - 180)
        angle *= -1
    elif 90 < robot_angle <= 180 and 0 < ball_angle <= 90:
    # Robot in Q1, Ball in Q2
        angle = ball_angle + (robot_angle - 180)
        angle *= -1
    elif 90 < robot_angle <= 180 and 90 < ball_angle <= 180 and abs(robot_angle) <= abs(ball_angle):
    # Both in Q1  (ball angle greater than robot angle)
        angle = ball_angle - robot_angle
    elif 90 < robot_angle <= 180 and 90 < ball_angle <= 180 and abs(robot_angle) >= abs(ball_angle):
    # Both in Q1 (robot angle greater than ball angle)
        angle = (abs(robot_angle) - abs(ball_angle)) * -1
    else:
        angle = 0
        print("Unhandled angle case")

    print(f"Final Angle: {angle} = Robot: {robot_angle}, Ball: {ball_angle}")


    print(f"Tip of the robot: {reference_point}")
    print(f"Destination: {destination_point}")
    print(f"Robot angle: {robot_angle}")
    print(f"Ball angle: {ball_angle}")
    print(f"Angle: {angle}")


    print(f"Distance: {distance},\n Ball Angle: {ball_angle},\n Robot Angle: {robot_angle}")

    match iteration:
        case 0:
            if 0 < angle:
                    input = f"turn_right_deg({angle})\n"
            else:
                    input = f"turn_left_deg({abs(angle)})\n"
        case 1:
                input = f"drive_straight_mm({distance - 75})\n"
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
    
    if -180 <= robot_angle <= -90 and -180 <= goal_angle <= -90 and abs(robot_angle) <= abs(goal_angle):
    # Both in Quadrant 4 (ball angle greater than robot angle)
        angle = goal_angle - robot_angle
    elif -180 <= robot_angle <= -90 and -180 <= goal_angle <= -90 and abs(robot_angle) >= abs(goal_angle):
    # Both in Quadrant 4 (robot angle greater than ball angle)
        angle = (abs(robot_angle) - abs(goal_angle)) * -1
    elif -180 <= robot_angle <= -90 and -90 < goal_angle <= 0:
    # Robot in Q4, Ball in Q3
        angle = (abs(robot_angle) + abs(goal_angle)) * -1
    elif -180 <= robot_angle <= -90 and 0 < goal_angle <= 90:
    # Robot in Q4, Ball in Q2
        angle = (180 - abs(robot_angle)) + goal_angle
    elif -180 <= robot_angle <= -90 and 90 < goal_angle <= 180:
    # Robot in Q4, Ball in Q1
        angle = (180 - abs(robot_angle)) + (180 - goal_angle)
        angle *= -1

    elif -90 < robot_angle <= 0 and -180 <= goal_angle <= -90:
    # Robot in Q3, Ball in Q4
        angle = goal_angle - robot_angle
    elif -90 < robot_angle <= 0 and -90 < goal_angle <= 0 and abs(robot_angle) <= abs(goal_angle):
    # Both in Q3 (ball angle greater than robot angle)
        angle = goal_angle + robot_angle
    elif -90 < robot_angle <= 0 and -90 < goal_angle <= 0 and abs(robot_angle) >= abs(goal_angle):
    # Both in Q3 (robot angle greater than ball angle)
        angle = (abs(robot_angle) - abs(goal_angle)) * -1
    elif -90 < robot_angle <= 0 and 0 < goal_angle <= 90:
    # Robot in Q3, Ball in Q2
        angle = abs(robot_angle) + goal_angle
    elif -90 < robot_angle <= 0 and 90 < goal_angle <= 180:
    # Robot in Q3, Ball in Q1
        angle = (180 + robot_angle) + (180 - goal_angle)
        angle *= -1

    elif 0 < robot_angle <= 90 and -180 <= goal_angle <= -90:
    # Robot in Q2, Ball in Q4
        angle = (180 - abs(goal_angle)) + robot_angle
    elif 0 < robot_angle <= 90 and -90 < goal_angle <= 0:
    # Robot in Q2, Ball in Q3
        angle = (robot_angle + abs(goal_angle)) - 1
    elif 0 < robot_angle <= 90 and 0 < goal_angle <= 90 and abs(robot_angle) <= abs(goal_angle):
    # Both in Q2  (ball angle greater than robot angle)
        angle = goal_angle - robot_angle
    elif 0 < robot_angle <= 90 and 0 < goal_angle <= 90 and abs(robot_angle) >= abs(goal_angle):
    # Both in Q2 (robot angle greater than ball angle)
        angle = (abs(robot_angle) - abs(goal_angle)) * -1
    elif 0 < robot_angle <= 90 and 90 < goal_angle <= 180:
    # Robot in Q2, Ball in Q1
        angle = (goal_angle - robot_angle)

    elif 90 < robot_angle <= 180 and -180 <= goal_angle <= -90:
    # Robot in Q1, Ball in Q4
        angle = (180 - abs(goal_angle)) + (180 - robot_angle)
    elif 90 < robot_angle <= 180 and -90 < goal_angle <= 0:
    # Robot in Q1, Ball in Q3
        angle = (180 + goal_angle) + (robot_angle - 180)
        angle *= -1
    elif 90 < robot_angle <= 180 and 0 < goal_angle <= 90:
    # Robot in Q1, Ball in Q2
        angle = goal_angle + (robot_angle - 180)
        angle *= -1
    elif 90 < robot_angle <= 180 and 90 < goal_angle <= 180 and abs(robot_angle) <= abs(goal_angle):
    # Both in Q1  (ball angle greater than robot angle)
        angle = goal_angle - robot_angle
    elif 90 < robot_angle <= 180 and 90 < goal_angle <= 180 and abs(robot_angle) >= abs(goal_angle):
    # Both in Q1 (robot angle greater than ball angle)
        angle = (abs(robot_angle) - abs(goal_angle)) * -1
    else:
        angle = 0
        print("Unhandled angle case")


    print(f"Final Angle: {angle} = Robot: {robot_angle}, Ball: {goal_angle}")

    print(f"Tip of the robot: {reference_point}")
    print(f"Destination: {goal_point}")
    print(f"Robot angle: {robot_angle}")
    print(f"Goal angle: {goal_angle}")
    print(f"Angle: {angle}")

    match iteration:
        case 0:
            if 0 < angle:
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