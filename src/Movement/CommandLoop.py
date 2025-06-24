import math
import time

from PathFinding.ArrowVector import ArrowVector


def collect_balls(reference_point, destination_point, robot_angle, max_drive_mm=100, angle_threshold=20):
    """
    Generate a single command to move the robot toward the ball: either turn or drive, based on current orientation and distance.

    Args:
        reference_point (tuple): Current robot position (x, y).
        destination_point (tuple): Ball position (x, y).
        robot_angle (float): Current robot orientation in degrees.
        max_drive_mm (float): Maximum distance to drive in one command.
        angle_threshold (float): Minimum angle (deg) to trigger a turn instead of driving.

    Returns:
        str or None: Command string for the robot, or None if already within 50mm.
    """
    print("Moving to collect balls (feedback mode)...")
    print("[DEBUG] collect_balls called with:")
    print(f"  reference_point: {reference_point}")
    print(f"  destination_point: {destination_point}")
    print(f"  robot_angle: {robot_angle}")
    print(f"  max_drive_mm: {max_drive_mm}, angle_threshold: {angle_threshold}")

    if reference_point is None or destination_point is None:
        print("[DEBUG] Either reference_point or destination_point is None. Returning None.")
        return None
    
    vector = ArrowVector(reference_point, destination_point)
    distance = vector.get_size()
    ball_angle = vector.get_angle()

    # Compute angle difference (normalize to [-180, 180])
    angle_diff = ball_angle - robot_angle
    angle_diff = (angle_diff + 180) % 360 - 180

    print(f"robot_angle: {robot_angle}, ball_angle: {ball_angle}, angle_diff: {angle_diff}")
    print(f"Distance to ball: {distance}")
    print(f"[DEBUG] robot_angle: {robot_angle}, ball_angle: {ball_angle}, angle_diff: {angle_diff}")
    print(f"[DEBUG] Distance to ball: {distance}")

    if distance <= 50:
        print("Already within 50mm of the ball. No command needed.")
        print("[DEBUG] Already within 50mm of the ball. No command needed. Returning None.")
        return None

    # If not facing the ball, turn first
    if abs(angle_diff) > angle_threshold:
        if angle_diff > 0:
            command = f"turn_left_deg({abs(angle_diff)})\n"
        else:
            command = f"turn_right_deg({abs(angle_diff)})\n"
        print(f"Turning: {command.strip()}")
        print(f"[DEBUG] Turning: {command.strip()}")
        return command
    else:
        # Drive forward, but not past the ball (stop at 50mm away)
        drive_dist = min(max_drive_mm, max(0, distance - 50))
        print(f"[DEBUG] drive_dist: {drive_dist}")
        if drive_dist > 0:
            command = f"drive_straight_mm({drive_dist})\n"
            print(f"Driving: {command.strip()}")
            print(f"[DEBUG] Driving: {command.strip()}")
            return command
        else:
            print("No drive needed (already close enough).")
            print("[DEBUG] No drive needed (already close enough). Returning None.")
            return None

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
    print("[DEBUG] move_to_goal called with:")
    print(f"  reference_point: {reference_point}")
    print(f"  goal_point: {goal_point}")
    print(f"  robot_angle: {robot_angle}")
    print(f"  iteration: {iteration}")

    if reference_point is None or goal_point is None:
        print("[DEBUG] Either reference_point or goal_point is None. Returning None.")
        return None

    vector = ArrowVector(reference_point, goal_point)
    distance = vector.get_size()
    goal_angle = vector.get_angle()
    print(f"[DEBUG] Calculated vector: distance={distance}, goal_angle={goal_angle}")
    
    if -180 <= robot_angle <= -90 and -180 <= goal_angle <= -90 and abs(robot_angle) <= abs(goal_angle):
    # Both in Quadrant 4 (ball angle greater than robot angle)
        angle = goal_angle + robot_angle
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
        angle = goal_angle + robot_angle
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
    print(f"Goal angle: {goal_angle}")
    print(f"Angle: {angle}")

    match iteration:
        case 0:
            if 0 < angle:
                    input = f"turn_right_deg({angle})\n"
            else:
                    input = f"turn_left_deg({abs(angle)})\n"
            print(f"[DEBUG] Iteration 0: {input.strip()}")
        case 1:
                input = f"drive_straight_mm({distance - 50})\n"
                print(f"[DEBUG] Iteration 1: {input.strip()}")
        case 2:
                input = f"stop_drive()\n"
                print(f"[DEBUG] Iteration 2: {input.strip()}")
        case 3:
                input = f"open_gate()\n"
                print(f"[DEBUG] Iteration 3: {input.strip()}")
        case 4:
                input = f"push_out()\n"
                print(f"[DEBUG] Iteration 4: {input.strip()}")
        case 5:
                input = f"push_return()\n"
                print(f"[DEBUG] Iteration 5: {input.strip()}")
        case 6:
                input = f"drive_straight_mm({-50})\n"
                print(f"[DEBUG] Iteration 6: {input.strip()}")
        case 7:
                input = f"close_gate()\n"   
                print(f"[DEBUG] Iteration 7: {input.strip()}")
    print(f"[DEBUG] Returning input: {input.strip()}")
    return input