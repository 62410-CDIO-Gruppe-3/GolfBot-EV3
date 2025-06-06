"""
tests/test_calibration.py – Test af farve- og homografikalibrering for GolfBot-EV3
"""

import cv2
import numpy as np
import os
from ImageRecognition.calibration import calibrate_color_range, calibrate_homography

def test_calibrate_color_range(image_path):
    print(f"Tester farvekalibrering på: {image_path}")
    img = cv2.imread(image_path)
    assert img is not None, f"Kunne ikke indlæse billede: {image_path}"
    lower, upper = calibrate_color_range(img)
    print(f"Valgte HSV-lower: {lower}, HSV-upper: {upper}")
    assert lower.shape == (3,) and upper.shape == (3,), "HSV-grænser har forkert format"

def test_calibrate_homography(image_path):
    print(f"Tester homografikalibrering på: {image_path}")
    img = cv2.imread(image_path)
    assert img is not None, f"Kunne ikke indlæse billede: {image_path}"

    # Dummy punkter – udskift med faktiske punkter fra din bane
    points_src = [(100, 100), (500, 100), (500, 400), (100, 400)]
    points_dst = [(0, 0), (1800, 0), (1800, 1200), (0, 1200)]
    H = calibrate_homography(img, points_src, points_dst)
    print(f"Homografi-matrix:\n{H}")
    assert H.shape == (3, 3), "Homografi-matrix har forkert format"

if __name__ == "__main__":
    test_image_path = os.path.join("assets", "test_image0.jpg")
    test_calibrate_color_range(test_image_path)
    test_calibrate_homography(test_image_path)