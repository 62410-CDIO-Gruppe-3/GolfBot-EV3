import sys
import os

sys.path.append(r"C:\\Users\\hatal\\GolfBot-EV3\\src")

from ImageRecognition.Homography        import load_homography, create_homography
from ImageRecognition.BallDetection     import detect_balls
from ImageRecognition.TransformBalls    import transform_balls
from ImageRecognition.ImageHomography   import get_homography_matrix
from ImageRecognition.ImagePoints       import get_transformed_points_from_image

assets_dir = r"C:\\Users\\hatal\\GolfBot-EV3\\src\\assets"
image_files = [f for f in os.listdir(assets_dir) if f.lower().endswith('.jpg')]
image = image_files[0] if image_files else None
image_files.sort()
img_path = "C:\\Users\\hatal\\GolfBot-EV3\\src\\assets\\test_image7.jpg"

H = get_homography_matrix(img_path)
print("Homography matrix:\n", H)

# Show transformed image
import cv2
import matplotlib.pyplot as plt
print("Reading image:", img_path)
img = cv2.imread(img_path)
if img is None:
    raise ValueError(f"Could not read image: {image}")
points = get_transformed_points_from_image(img_path)
print("Points generated from image:\n", points)
img_transformed = cv2.warpPerspective(img, H, (1800, 1200))
cv2.imwrite("C:\\Users\\hatal\\GolfBot-EV3\\src\\assets\\transformed_image.jpg", img_transformed)
transformed_path = "C:\\Users\\hatal\\GolfBot-EV3\\src\\assets\\transformed_image.jpg"
plt.imshow(cv2.cvtColor(img_transformed, cv2.COLOR_BGR2RGB))
plt.title("Transformed Image")
plt.axis('off')
plt.show()