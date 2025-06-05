"""
image_utils.py – Hjælpefunktioner til billedbehandling for GolfBot-EV3
Kan bruges til at forbedre billeder før boldgenkendelse eller anden analyse.
"""

import cv2
import numpy as np

def enhance_contrast(image):
    """
    Forbedrer kontrasten i et billede (gråskala).
    Kan bruges før boldgenkendelse eller anden billedanalyse.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    enhanced = cv2.equalizeHist(gray)
    return enhanced

def apply_gaussian_blur(image, kernel_size=(5, 5)):
    """
    Anvender Gaussian blur for at reducere støj i billedet.
    """
    return cv2.GaussianBlur(image, kernel_size, 0)

def threshold_image(image, thresh=127):
    """
    Binariserer billedet med en fast tærskelværdi.
    """
    _, binary = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)
    return binary

# Eksempel på brug:
if __name__ == "__main__":
    img = cv2.imread("test_images/banebillede.jpg")
    if img is not None:
        enhanced = enhance_contrast(img)
        blurred = apply_gaussian_blur(enhanced)
        binary = threshold_image(blurred)
        cv2.imshow("Enhanced", enhanced)
        cv2.imshow("Blurred", blurred)
        cv2.imshow("Binary", binary)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Kunne ikke indlæse testbillede.")