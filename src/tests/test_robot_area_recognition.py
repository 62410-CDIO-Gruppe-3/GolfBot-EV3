"""
tests/test_robot_area_recognition.py – Test af RobotAreaRecognition.py for GolfBot-EV3
"""

import os
import cv2
from ImageRecognition.RobotAreaRecognition import detect_rectangles

def test_detect_rectangles(image_path, expect_rects=True):
    image = cv2.imread(image_path)
    assert image is not None, f"Kunne ikke indlæse billede: {image_path}"

    rectangles = detect_rectangles(image)
    print(f"\nTest af: {os.path.basename(image_path)}")
    print(f"Antal fundne rektangler: {len(rectangles)}")

    if expect_rects:
        assert len(rectangles) > 0, "Forventede at finde mindst ét rektangel, men fandt ingen."
    else:
        assert len(rectangles) == 0, "Forventede ingen rektangler, men fandt nogle."

    # Vis resultat
    image_vis = image.copy()
    for rect in rectangles:
        cv2.polylines(image_vis, [rect], isClosed=True, color=(0, 255, 0), thickness=3)
    cv2.imshow("Rektangel-detektion", image_vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    assets_dir = os.path.join("assets")
    test_cases = [
        ("test_image0.jpg", True),
        ("test_image99.jpg", False)  # Antag ingen rektangler på dette billede
    ]
    for filename, expect_rects in test_cases:
        image_path = os.path.join(assets_dir, filename)
        if os.path.exists(image_path):
            test_detect_rectangles(image_path, expect_rects)
        else:
            print(f"Testbillede ikke fundet: {image_path}")