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
from track_robot_v2 import get_robot_pose
from Movement.AutonomousClient import send_and_receive, collect_VIP_ball, repeat_collection, robot_move_to_goal

API_KEY = "BdmadiDKNX7YzP4unsUm"
TRANSFORM_W, TRANSFORM_H = 1200, 1800
HOMOGRAPHY_FILE = ROOT.parent / "homography.npy"

CONFIG = InferenceConfig(
    api_url="http://localhost:9001",
    api_key=API_KEY,
    model_id="tabletennis-ball-detection/1",
)
detections = None

def main() -> None:
    global detections
    try:
        H = load_homography(HOMOGRAPHY_FILE)
    except Exception as exc:  # pragma: no cover - runtime path issue
        print(f"Could not load homography: {exc}")
        return

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():  # pragma: no cover - runtime only
        print("Failed to open camera")
        return

    mode = "collect"
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = run_inference(frame_rgb, CONFIG)
        if detections is None:
            detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
        transformed = transform_points(detections, H) if detections else []

        print(f"Detected {len(transformed)} points")
        print(f"Transformed points: {transformed}")

        goal_point = (1100, 900)
        pose = get_robot_pose(frame)
        print(f"Robot position: {pose}")
        (temp_x, temp_y), _ = pose

        if pose:
            transformed_robot_pose = transform_points([(temp_x, temp_y)], H)
            if transformed_robot_pose.any():
                (tx, ty) = transformed_robot_pose[0]
                print(f"Transformed robot position: {(tx, ty)}")

        if pose and transformed is not None and len(transformed) > 0:
            (cx, cy), robot_angle = pose

            print(f"Robot position: {(cx,cy)}")
            print(f"Robot angle: {robot_angle}")
            if mode == "collect":
                closest = min(
                    transformed,
                    key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2,
                )
                print(f"Closest point: {closest}")
                for i in range(6):
                    collect_VIP_ball((cx, cy), closest, robot_angle=robot_angle, iteration=i)
                    time.sleep(1)
                mode = "move"
                continue  # Skip to next frame after collect
            elif mode == "move":
                for i in range(8):
                    robot_move_to_goal((cx, cy), goal_point, robot_angle=robot_angle, iteration=i)
                    time.sleep(1)
                mode = "collect"
                continue  # Skip to next frame after move            (cx, cy), robot_angle = pose

        frame_disp = draw_points(frame, detections)
        cv2.imshow("Integrated", frame_disp)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
