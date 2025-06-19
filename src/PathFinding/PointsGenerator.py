import numpy as np
from ImageRecognition.ImagePoints import get_transformed_points_from_image
from ImageRecognition.ArrowDetection import detect_arrow_tip

def get_closest_path_point(destination_points, reference_point) -> tuple[int, int]:
    """
    Return the single closest point from 'points' relative to the 'reference' point.
    
    Args:
        points: A list of (x, y) tuples.
        reference: The reference (x, y) point.
        
    Returns:
        The (x, y) tuple from destination_points that is closest to the reference.
    """
    return min(destination_points, key=lambda p: (p[0] - reference_point[0])**2 + (p[1] - reference_point[1])**2)

# Example usage:
if __name__ == "__main__":
    # Get transformed points from ImageRecognition using the getter
    transformed_points = get_transformed_points_from_image()
    reference_point = detect_arrow_tip()  # Replace with your actual reference point
    closest_points = get_closest_path_point(transformed_points, reference_point)
    print(closest_points)