from ImageRecognition.Homography import create_homography, save_homography
from ImageRecognition.ImagePoints import get_transformed_points_from_image
from ImageRecognition.ArrowDetection import detect_arrow_tip, get_closest_path_points

from PathFinding.PointsGenerator import get_closest_path_points
from PathFinding.PathGenerator import get_arrow_vector_x, get_arrow_vector_y, get_arrow_vector_angle, get_arrow_vector_size

def collect_balls(image, arrow_template, transformed_points):
    """
    Create an input dictionary for the pathfinding algorithm.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        dict: Input dictionary containing transformed points and arrow vectors.
    """
    transformed_points = get_transformed_points_from_image(image, transformed_points)
    tip = detect_arrow_tip(image, arrow_template)

    if tip is None or transformed_points is None or len(transformed_points) == 0:
        return None
    
    input = ""

    closest = get_closest_path_points(transformed_points, tip, num_points=1)[0]
    dx = get_arrow_vector_x(image, arrow_template, closest)
    dy = get_arrow_vector_y(image, arrow_template, closest)
    angle = get_arrow_vector_angle(image, arrow_template, transformed_points)
    distance = get_arrow_vector_size(image, arrow_template, transformed_points)

    if angle is range(5, 180):
        input += f"turn_left_deg({angle})\n"
    elif angle is range(185, 360):
        input += f"turn_right_deg({angle})\n"

    input += f"drive_straight_mm({distance - 50})\n"

    input += f"open_gate()\n"

    input += f"drive_straight_mm(50)\n"

    input += f"close_gate()\n"

    return input

def move_to_goal(image, arrow_template, goal_point):
    """
    Create an input dictionary for the pathfinding algorithm to move to the goal.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        dict: Input dictionary containing transformed points and arrow vectors.
    """
    tip = detect_arrow_tip(image, arrow_template)

    if tip is None or goal_point is None:
        return None
    
    input = ""

    angle = get_arrow_vector_angle(image, arrow_template, goal_point)
    distance = get_arrow_vector_size(image, arrow_template, goal_point)

    if angle is range(5, 180):
        input += f"turn_left_deg({angle})\n"
    elif angle is range(185, 360):
        input += f"turn_right_deg({angle})\n"
    
    input += f"drive_straight_mm({distance - 5})\n"
    input += f"open_gate()\n"
    input += f"push_out()\n"
    input += f"push_return()\n"

    return input

