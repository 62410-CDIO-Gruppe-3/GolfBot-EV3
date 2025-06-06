"""
tests/test_image_utils.py – Test af image_utils.py for GolfBot-EV3
Tester kontrastforbedring, Gaussian blur og thresholding på testbilleder.
"""

import cv2
import numpy as np
import os
from ImageRecognition.image_utils import enhance_contrast, apply_gaussian_blur, threshold_image

def test_image_utils(image_path):
    print(f"Tester image_utils på: {image_path}")
    img = cv2.imread(image_path)
    assert img is not None, f"Kunne ikke indlæse billede: {image_path}"

    # Test kontrastforbedring
    enhanced = enhance_contrast(img)
    assert enhanced is not None and enhanced.shape == img.shape[:2], "Kontrastforbedring fejlede"

    # Test Gaussian blur
    blurred = apply_gaussian_blur(enhanced)
    assert blurred is not None and blurred.shape == enhanced.shape, "Gaussian blur fejlede"

    # Test thresholding
    binary = threshold_image(blurred)
    assert binary is not None and binary.shape == blurred.shape, "Thresholding fejlede"

    # Vis resultater
    cv2.imshow("Original", img)
    cv2.imshow("Enhanced", enhanced)
    cv2.imshow("Blurred", blurred)
    cv2.imshow("Binary", binary)
    print("Tryk på en vilkårlig tast for at fortsætte...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Brug et testbillede fra assets-mappen
    test_image_path = os.path.join("assets", "test_image0.jpg")
    test_image_utils(test_image_path)