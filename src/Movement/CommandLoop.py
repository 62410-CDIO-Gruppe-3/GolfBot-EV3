import math

from PathFinding.ArrowVector import ArrowVector

# Constants for movement control
TURN_THRESHOLD_DEG = 20
MAX_DRIVE_MM = 100
BALL_PROXIMITY_MM = 75  # How close to get to the ball before collection
GOAL_PROXIMITY_MM = 50  # How close to get to the goal before dropping


def _calculate_turn_angle(robot_angle, target_angle):
    """Calculates the shortest angle for the robot to turn."""
    turn_angle = target_angle - robot_angle
    # Normalize angle to -180, 180
    while turn_angle > 180:
        turn_angle -= 360
    while turn_angle < -180:
        turn_angle += 360
    return turn_angle


def get_command_to_ball(reference_point, destination_point, robot_angle):
    """
    Generates a single command to move towards a ball.
    Returns a movement command string, or None if at the destination.
    """
    if reference_point is None or destination_point is None:
        return None

    vector = ArrowVector(reference_point, destination_point)
    distance = vector.get_size()
    target_angle = vector.get_angle()

    # If we are close enough, signal to start collection
    if distance <= BALL_PROXIMITY_MM:
        return None

    turn_angle = _calculate_turn_angle(robot_angle, target_angle)

    print(f"Robot Angle: {robot_angle:.2f}, Ball Angle: {target_angle:.2f}, Turn Angle: {turn_angle:.2f}, Distance: {distance:.2f}")

    # Stepwise scaling of max turn angle based on distance to ball
    if distance > 2 * BALL_PROXIMITY_MM:
        max_turn_deg = 30
    elif distance > 1.5 * BALL_PROXIMITY_MM:
        max_turn_deg = 10
    else:
        max_turn_deg = 5
    max_turn_deg = max(max_turn_deg, 5)  # Never allow less than 5 deg unless actual turn is less

    # If we need to turn more than the threshold, send a turn command
    if abs(turn_angle) > TURN_THRESHOLD_DEG:
        turn_amount = min(abs(turn_angle), max_turn_deg)
        if turn_angle > 0:
            return f"turn_left_deg({turn_amount:.2f})\n"
        else:
            return f"turn_right_deg({turn_amount:.2f})\n"
    
    # Drive forward and do ball collection using the existing function
    drive_dist = min(MAX_DRIVE_MM, distance - BALL_PROXIMITY_MM)
    return (
        f"drive_straight_mm({drive_dist:.2f})\n"
    )


def get_ball_collection_sequence():
    """Returns the sequence of commands to collect a ball."""
    return [
        "open_gate()\n",
        f"drive_straight_mm(50)\n",
        "stop_drive()\n",
        "close_gate()\n",
    ]


def get_command_to_goal(reference_point, goal_point, robot_angle):
    """
    Generates a single command to move towards the goal.
    Returns a movement command string, or None if at the destination.
    """
    if reference_point is None or goal_point is None:
        return None

    vector = ArrowVector(reference_point, goal_point)
    distance = vector.get_size()
    target_angle = vector.get_angle()

    # If we are close enough, signal to start drop-off
    if distance <= GOAL_PROXIMITY_MM:
        return None

    turn_angle = _calculate_turn_angle(robot_angle, target_angle)

    print(f"Robot Angle: {robot_angle:.2f}, Goal Angle: {target_angle:.2f}, Turn Angle: {turn_angle:.2f}, Distance: {distance:.2f}")

    # If we need to turn more than the threshold, send a turn command
    if abs(turn_angle) > TURN_THRESHOLD_DEG:
        turn_amount = min(abs(turn_angle), 30)
        if turn_angle > 0:
            return f"turn_right_deg({turn_amount:.2f})\n"
        else:
            return f"turn_left_deg({turn_amount:.2f})\n"

    # Otherwise, drive forward
    drive_dist = min(MAX_DRIVE_MM, distance - GOAL_PROXIMITY_MM)
    return f"drive_straight_mm({drive_dist:.2f})\n"


def get_goal_drop_off_sequence():
    """Returns the sequence of commands to drop off balls at the goal."""
    return [
        "stop_drive()\n",
        "open_gate()\n",
        "push_out()\n",
        "push_return()\n",
        "drive_straight_mm(-50)\n",
        "close_gate()\n",
    ]