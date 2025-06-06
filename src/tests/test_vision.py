"""
tests/test_vision.py – Udvidet test af boldgenkendelse med vision.py
"""

import os
import cv2
from vision import BallDetector

def test_detect_balls_and_vip(image_path, expect_balls=True, expect_vip=False):
    detector = BallDetector()
    frame = cv2.imread(image_path)
    assert frame is not None, f"Kunne ikke indlæse billede: {image_path}"

    balls = detector.detect_balls(frame)
    vip = detector.detect_vip(frame)

    print(f"\nTest af: {os.path.basename(image_path)}")
    print(f"Fundne bolde: {balls}")
    print(f"VIP-bold: {vip}")

    if expect_balls:
        assert len(balls) > 0, "Forventede at finde mindst én bold, men fandt ingen."
    else:
        assert len(balls) == 0, "Forventede ingen bolde, men fandt nogle."

    if expect_vip:
        assert vip is not None, "Forventede at finde VIP-bold, men fandt ingen."
    else:
        assert vip is None, "Forventede ikke VIP-bold, men fandt én."

if __name__ == "__main__":
    # Test med flere billeder fra assets/
    assets_dir = os.path.join("assets")
    test_cases = [
        ("test_image0.jpg", True, False),
        ("test_image1.jpg", True, True),   # Antag VIP-bold på dette billede
        ("test_image99.jpg", False, False) # Antag dette billede har ingen bolde
    ]
    for filename, expect_balls, expect_vip in test_cases:
        image_path = os.path.join(assets_dir, filename)
        if os.path.exists(image_path):
            test_detect_balls_and_vip(image_path, expect_balls, expect_vip)
        else:
            print(f"Testbillede ikke fundet: {image_path}")