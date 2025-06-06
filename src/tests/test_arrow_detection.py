"""
tests/test_arrow_detection.py – Test af ArrowDetection.py for GolfBot-EV3
"""

import os
import cv2
import numpy as np
from ImageRecognition.ArrowDetection import detect_arrow_tip

def test_detect_arrow_tip(image_path, template_path, expect_tip=True):
    image = cv2.imread(image_path)
    arrow_template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    assert image is not None, f"Kunne ikke indlæse billede: {image_path}"
    assert arrow_template is not None, f"Kunne ikke indlæse pil-template: {template_path}"

    tip = detect_arrow_tip(image, arrow_template)
    print(f"\nTest af: {os.path.basename(image_path)} med template {os.path.basename(template_path)}")
    print(f"Fundet pil-tip: {tip}")

    if expect_tip:
        assert tip is not None, "Forventede at finde pil-tip, men fandt ingen."
        # Vis resultat
        image_vis = image.copy()
        cv2.circle(image_vis, tip, 10, (0, 0, 255), -1)
        cv2.imshow("Pil-tip detektion", image_vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        assert tip is None, "Forventede ikke pil-tip, men fandt én."

if __name__ == "__main__":
    assets_dir = os.path.join("assets")
    # Tilføj dit pil-template-billede til assets/ og brug det her
    test_cases = [
        ("test_image0.jpg", "arrow_template.jpg", True),
        ("test_image99.jpg", "arrow_template.jpg", False)  # Antag ingen pil på dette billede
    ]
    for filename, template, expect_tip in test_cases:
        image_path = os.path.join(assets_dir, filename)
        template_path = os.path.join(assets_dir, template)
        if os.path.exists(image_path) and os.path.exists(template_path):
            test_detect_arrow_tip(image_path, template_path, expect_tip)
        else:
            print(f"Testbillede eller template ikke fundet: {image_path}, {template_path}")