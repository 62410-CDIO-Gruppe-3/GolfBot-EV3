"""
vision.py – Boldgenkendelse til GolfBot-EV3
Bruger OpenCV til at finde og markere bolde samt udpege VIP-bolden (orange).
"""

import cv2
import numpy as np
from config import VISION_CAMERA_ID, VISION_FRAME_WIDTH, VISION_FRAME_HEIGHT

class BallDetector:
    def __init__(self, camera_id=VISION_CAMERA_ID, width=VISION_FRAME_WIDTH, height=VISION_FRAME_HEIGHT):
        self.camera_id = camera_id
        self.width = width
        self.height = height

    def stream_from_camera(self):
        cap = cv2.VideoCapture(self.camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if not cap.isOpened():
            raise RuntimeError("Kan ikke åbne kamera.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Ingen billede fra kamera.")
                break
            balls = self.detect_balls(frame)
            vip = self.detect_vip(frame)
            # Tegn bolde
            for (x, y) in balls:
                cv2.circle(frame, (x, y), 20, (0, 255, 0), 2)
            # Tegn VIP-bold
            if vip:
                cv2.circle(frame, vip, 25, (0, 140, 255), 4)
                cv2.putText(frame, "VIP", (vip[0]-10, vip[1]-30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,140,255), 2)
            cv2.imshow("GolfBot Ball Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def detect_balls(self, frame):
        """Returnerer liste af (x, y) for alle hvide bolde."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Hvid bold: justér evt. værdier for din belysning
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 60, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        balls = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100:  # Minimum areal for at filtrere støj
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    balls.append((cx, cy))
        return balls

    def detect_vip(self, frame):
        """Returnerer (x, y) for VIP-bolden (orange), ellers None."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Orange farveområde (justér efter behov)
        lower_orange = np.array([5, 100, 100])
        upper_orange = np.array([20, 255, 255])
        mask = cv2.inRange(hsv, lower_orange, upper_orange)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        vip = None
        max_area = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100 and area > max_area:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    vip = (cx, cy)
                    max_area = area
        return vip

# Eksempel på brug:
if __name__ == "__main__":
    detector = BallDetector()
    detector.stream_from_camera()