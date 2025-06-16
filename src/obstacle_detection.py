"""
obstacle_detection.py – Detektion af forhindringer på banen (f.eks. midterkors) til GolfBot-EV3
Bruger OpenCV til at finde faste forhindringer og returnerer deres koordinater.
"""

import cv2
import numpy as np

def detect_obstacles(frame):
    """
    Detects obstacles (like the cross) in the given image frame and returns their coordinates.
    Args:
        frame (np.ndarray): Input image (BGR).
    Returns:
        list of dict: [{'type': 'cross', 'x': int, 'y': int, 'width': int, 'height': int}, ...]
    """
    obstacles = []

    # Konverter til HSV for robust farvefiltrering
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Definér farveområde for sort (justér evt. til din bane)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 40])

    mask = cv2.inRange(hsv, lower_black, upper_black)

    # Find konturer af forhindringer
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # Filtrér små objekter fra
            x, y, w, h = cv2.boundingRect(cnt)
            obstacles.append({
                'type': 'cross',
                'x': int(x),
                'y': int(y),
                'width': int(w),
                'height': int(h)
            })

    return obstacles

# Eksempel på brug:
if __name__ == "__main__":
    img = cv2.imread("assets/test_image0.jpg")
    if img is not None:
        obstacles = detect_obstacles(img)
        print("Fundne forhindringer:", obstacles)
        # Visualisering
        for obs in obstacles:
            cv2.rectangle(img, (obs['x'], obs['y']), (obs['x']+obs['width'], obs['y']+obs['height']), (0,0,255), 2)
        cv2.imshow("Obstacle Detection", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Kunne ikke indlæse testbillede.")