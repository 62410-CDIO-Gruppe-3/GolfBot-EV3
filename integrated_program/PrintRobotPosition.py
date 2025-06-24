from pathlib import Path
import sys
import cv2
import numpy as np
import time

# Allow imports from the src directory
ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.append(str(ROOT))

from cdio_utils import InferenceConfig, run_inference, transform_points, draw_points
from ImageRecognition.Homography import load_homography
from test_robot_v2 import get_robot_pose

API_KEY = "BdmadiDKNX7YzP4unsUm"
TRANSFORM_W, TRANSFORM_H = 1800, 1200
HOMOGRAPHY_FILE = ROOT.parent / "homography.npy"

def main() -> None:
    try:
        H = load_homography(HOMOGRAPHY_FILE)
    except Exception as exc:  # pragma: no cover - runtime path issue
        print(f"Could not load homography: {exc}")
        return

    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened():  # pragma: no cover - runtime only
        print("Failed to open camera")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        position = get_robot_pose(frame)
        (cx, cy), robot_angle = position if position else (None, None), None

        print(f"Robot position: {(cx,cy)}\n Robot angle: {robot_angle}")

        frame_disp = draw_points(frame, (cx, cy)) if position else frame.copy()
        cv2.imshow("Integrated", frame_disp)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
