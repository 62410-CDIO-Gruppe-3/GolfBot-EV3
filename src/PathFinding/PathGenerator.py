import sys
sys.path.append(r"C:\\Users\\hatal\\GolfBot-EV3\\src")

from PathFinding.PointsGenerator import get_closest_path_points
from ImageRecognition.ImagePoints import get_transformed_points_from_image
from ImageRecognition.ArrowDetection import detect_arrow_tip

def get_arrow_vector(image, arrow_template, transformed_points):
    """
    Returns a vector (dx, dy) from the arrow tip to the closest transformed point.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        tuple: ((tip_x, tip_y), (closest_x, closest_y), (dx, dy)) or None if not found.
    """

    transformed_points = get_transformed_points_from_image(image, transformed_points)

    tip = detect_arrow_tip(image, arrow_template)
    if tip is None or transformed_points is None or len(transformed_points) == 0:
        return None

    closest = get_closest_path_points(transformed_points, tip, num_points=1)[0]
    dx = closest[0] - tip[0]
    dy = closest[1] - tip[1]
    return (tip, closest, (dx, dy))

def get_arrow_vector_x(image, arrow_template, transformed_points):
    """
    Returns the x component (dx) of the vector from the arrow tip to the closest transformed point.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        float or None: The x component (dx) of the vector, or None if not found.
    """
    result = get_arrow_vector(image, arrow_template, transformed_points)
    if result is None:
        return None
    _, _, (dx, _) = result
    return dx

def get_arrow_vector_y(image, arrow_template, transformed_points):
    """
    Returns the x component (dx) of the vector from the arrow tip to the closest transformed point.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        float or None: The x component (dx) of the vector, or None if not found.
    """
    result = get_arrow_vector(image, arrow_template, transformed_points)
    if result is None:
        return None
    _, _, (dy, _) = result
    return dy

def get_arrow_vector_size(image, arrow_template, transformed_points):
    """
    Returns the size of the vector from the arrow tip to the closest transformed point.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        float or None: The size of the vector, or None if not found.
    """
    result = get_arrow_vector(image, arrow_template, transformed_points)
    if result is None:
        return None
    _, _, (dx, dy) = result
    return (dx**2 + dy**2)**0.5

def get_arrow_vector_angle(image, arrow_template, transformed_points):
    """
    Returns the angle of the vector from the arrow tip to the closest transformed point.

    Args:
        image (np.ndarray): The input image (BGR).
        arrow_template (np.ndarray): Grayscale arrow template image.
        transformed_points (list or np.ndarray): List of (x, y) points.

    Returns:
        float or None: The angle of the vector in radians, or None if not found.
    """
    result = get_arrow_vector(image, arrow_template, transformed_points)
    if result is None:
        return None
    _, _, (dx, dy) = result
    return np.arctan2(dy, dx)