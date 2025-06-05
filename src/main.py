import sys
sys.path.append(r"C:\\Users\\hatal\\GolfBot-EV3\\src")

from ImageRecognition.ImageRecognition import get_transformed_points_from_image
from PathFinding.PathGenerator import get_closest_path_points

def main():
    # Run image recognition to get transformed points
    transformed_points = get_transformed_points_from_image()
    # Define your reference point (change as needed)
    reference_point = (0, 0)
    # Get the five closest path points
    closest_points = get_closest_path_points(transformed_points, reference_point)
    print("Five closest path points:", closest_points)

if __name__ == "__main__":
    main()