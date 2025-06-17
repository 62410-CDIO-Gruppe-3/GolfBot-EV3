import sys
sys.path.append("C:\\Users\\hatal\\GolfBot-EV3\\src")


from ImageRecognition.ImagePoints import get_transformed_points_from_image
from ImageRecognition.ArrowDetection import detect_arrow_tip

from PathFinding.PointsGenerator import get_closest_path_point
from PathFinding.ArrowVector import ArrowVector


def collect_balls(reference_point, destination_points):
    """
    Create an input dictionary for the pathfinding algorithm.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        dict: Input dictionary containing transformed points and arrow vectors.
    """

    tip = reference_point

    if tip is None or destination_points is None or len(destination_points) == 0:
        return None

    closest = get_closest_path_point(destination_points, tip)
    vector = ArrowVector(tip, closest)
    distance = vector.get_size()
    angle = vector.get_angle()
    normalized_angle = angle % 360  # Normalize angle to [0, 360)

    print("Tip of the robot: ", tip, "\n Destination: ", closest)

    print(f"Distance: {distance}, Angle: {angle}, Normalized Angle: {normalized_angle}")

    if normalized_angle < 180:
        input = f"turn_left_deg({normalized_angle})\n"
    else:
        input = f"turn_right_deg({normalized_angle})\n"

    input += f"drive_straight_mm({distance - 50})\n"

    input += f"open_gate()\n"

    input += f"drive_straight_mm({50})\n"

    input += f"close_gate()\n"

    print(f"CommandLoop: Remaining destination points: {destination_points}", 
          "\n Length of destination points:", len(destination_points), 
          "\n Removed former closest point:", closest)

    return input

def move_to_goal(reference_point, goal_point):
    """
    Create an input dictionary for the pathfinding algorithm to move to the goal.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        dict: Input dictionary containing transformed points and arrow vectors.
    """

    tip = reference_point

    if tip is None or goal_point is None:
        return None

    vector = ArrowVector(tip, goal_point)
    distance = vector.get_size()
    angle = vector.get_angle()
    normalized_angle = (angle + 360) % 360  # Normalize angle to [0, 360)

    print("Tip of the robot: ", tip, "\n Goal: ", goal_point)
     
    print(f"Distance: {distance}, Angle: {angle}, Normalized Angle: {normalized_angle}")

    if normalized_angle < 180:
        input = f"turn_left_deg({normalized_angle})\n"
    else:
        input = f"turn_right_deg({normalized_angle})\n"
    
    input += f"drive_straight_mm({distance - 5})\n"

    input += f"open_gate()\n"

    input += f"push_out()\n"

    input += f"push_return()\n"
    
    input += f"close_gate()\n"

    return input