"""
calibration.py – Kamera- og farvekalibrering for GolfBot-EV3
Indeholder funktioner til at kalibrere kameraets farver og homografi.
"""

import cv2
import numpy as np

def calibrate_color_range(image, window_name="Kalibrér farve"):
    """
    Interaktivt værktøj til at finde HSV-farvegrænser for fx bold eller VIP-bold.
    Brug trackbars til at justere og find optimale værdier.
    """
    def nothing(x):
        pass

    cv2.namedWindow(window_name)
    cv2.createTrackbar('H Low', window_name, 0, 179, nothing)
    cv2.createTrackbar('H High', window_name, 179, 179, nothing)
    cv2.createTrackbar('S Low', window_name, 0, 255, nothing)
    cv2.createTrackbar('S High', window_name, 255, 255, nothing)
    cv2.createTrackbar('V Low', window_name, 0, 255, nothing)
    cv2.createTrackbar('V High', window_name, 255, 255, nothing)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    while True:
        h_low = cv2.getTrackbarPos('H Low', window_name)
        h_high = cv2.getTrackbarPos('H High', window_name)
        s_low = cv2.getTrackbarPos('S Low', window_name)
        s_high = cv2.getTrackbarPos('S High', window_name)
        v_low = cv2.getTrackbarPos('V Low', window_name)
        v_high = cv2.getTrackbarPos('V High', window_name)

        lower = np.array([h_low, s_low, v_low])
        upper = np.array([h_high, s_high, v_high])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(image, image, mask=mask)

        cv2.imshow(window_name, result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    print(f"Lower HSV: {lower}")
    print(f"Upper HSV: {upper}")
    return lower, upper

def calibrate_homography(image, points_src, points_dst):
    """
    Beregner homografi-matrix ud fra fire kild- og fire destinationspunkter.
    """
    pts_src = np.array(points_src, dtype="float32")
    pts_dst = np.array(points_dst, dtype="float32")
    H, status = cv2.findHomography(pts_src, pts_dst)
    return H

# Eksempel på brug:
if __name__ == "__main__":
    img = cv2.imread("test_images/banebillede.jpg")
    if img is not None:
        calibrate_color_range(img)
    else:
        print("Kunne ikke indlæse testbillede.")