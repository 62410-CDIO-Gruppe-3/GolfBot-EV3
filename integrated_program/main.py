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

SRC = Path(__file__).resolve().parents[1] / "src"

API_KEY = "BdmadiDKNX7YzP4unsUm"
TRANSFORM_W, TRANSFORM_H = 1800, 1200
HOMOGRAPHY_FILE = SRC / "homography.npy"

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
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened():  # pragma: no cover - runtime only
        print("Failed to open camera")
        return

    mode = "collect"
    pose_stable_count = 0
    POSE_STABLE_THRESHOLD = 3
    last_pose = None
    target_ball = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = run_inference(frame_rgb, CONFIG)
        print(f"Received inference result: {result}")
        print("Raw predictions:", result.get("predictions", []))
        if detections is None:
            filtered = [
                p for p in result.get("predictions", [])
                if p["confidence"] >= 0.2 and 10 <= p["width"] <= 200 and 10 <= p["height"] <= 200
            ]
        detections = [(p["x"], p["y"]) for p in filtered]
        print(f"[DEBUG] Detections: {detections}")
        transformed = transform_points(detections, H) if detections else []
        print(f"Detected {len(transformed)} points")
        print(f"Transformed points: {transformed}")
        print(f"[DEBUG] Transformed points: {transformed}")

        print(f"[DEBUG] mode: {mode}")
        goal_point = (100, 600)
        pose = get_robot_pose(frame, debug=False, homography=H)
        print(f"[DEBUG] pose: {pose}")

        if pose is not None:
            pose_stable_count += 1
            last_pose = pose
        else:
            pose_stable_count = 0
            last_pose = None

        if pose_stable_count < POSE_STABLE_THRESHOLD:
            print(f"[DEBUG] Waiting for stable pose... ({pose_stable_count}/{POSE_STABLE_THRESHOLD})")
            frame_disp = draw_points(frame, detections)
            cv2.imshow("Integrated", frame_disp)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue

        (cx, cy), robot_angle = last_pose
        if transformed is not None and len(transformed) > 0:
            print(f"Robot position: {(cx, cy)}")
            print(f"Robot angle: {robot_angle}")
            if mode == "collect":
                if target_ball is None:
                    target_ball = min(
                        transformed,
                        key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2,
                    )
                    print(f"[DEBUG] New target ball: {target_ball}")
                else:
                    print(f"[DEBUG] Continuing with target ball: {target_ball}")
                # Feedback-driven loop: keep updating position and sending commands until within 50mm
                while True:
                    # Re-capture frame for fresh position data
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to grab frame during collection")
                        break
                    pose = get_robot_pose(frame, debug=False, homography=H)
                    print(f"[DEBUG] pose (collect loop): {pose}")
                    if pose is not None:
                        pose_stable_count += 1
                        last_pose = pose
                    else:
                        pose_stable_count = 0
                        last_pose = None
                    if pose_stable_count < POSE_STABLE_THRESHOLD:
                        print(f"[DEBUG] Waiting for stable pose in collect loop... ({pose_stable_count}/{POSE_STABLE_THRESHOLD})")
                        continue
                    (cx, cy), robot_angle = last_pose
                    # Optionally, re-detect balls here if you want to update ball position
                    command_sent = collect_VIP_ball((cx, cy), target_ball, robot_angle=robot_angle, max_drive_mm=30.0)
                    print(f"[DEBUG] collect_VIP_ball returned: {command_sent}")
                    if not command_sent:
                        print("No more commands needed (within 50mm or cannot proceed).")
                        break
                target_ball = None  # Clear after collection
                mode = "move"
                print(f"[DEBUG] Switching mode to: {mode}")
                continue  # Skip to next frame after collect
            elif mode == "move":
                for i in range(8):
                    print(f"[DEBUG] robot_move_to_goal iteration: {i}")
                    robot_move_to_goal((cx, cy), goal_point, robot_angle=robot_angle, iteration=i)
                mode = "collect"
                print(f"[DEBUG] Switching mode to: {mode}")
                continue  # Skip to next frame after move            (cx, cy), robot_angle = pose

        frame_disp = draw_points(frame, detections)
        cv2.imshow("Integrated", frame_disp)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
