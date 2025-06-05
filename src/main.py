import sys
import os

sys.path.append(r"C:\\Users\\hatal\\GolfBot-EV3\\src")

from ImageRecognition.ImageRecognition import get_transformed_points_from_image
from PathFinding.PathGenerator import get_closest_path_points

def main():
    assets_dir = r"C:\\Users\\hatal\\GolfBot-EV3\\src\\assets"
    image_files = [f for f in os.listdir(assets_dir) if f.lower().endswith('.jpg')]
    image_files.sort()  # Optional: process in order

    for image_file in image_files:
        image_path = os.path.join(assets_dir, image_file)
        print(f"\nProcessing {image_path}")
        transformed_points = get_transformed_points_from_image(image_path)
        reference_point = (0, 0)
        closest_points = get_closest_path_points(transformed_points, reference_point)
        print("Five closest path points:", closest_points)

if __name__ == "__main__":
    main()