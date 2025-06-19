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


def main() -> None:
    try:
        H = load_homography(HOMOGRAPHY_FILE)
    except Exception as exc:  # pragma: no cover - runtime path issue
        print(f"Could not load homography: {exc}")
        return

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():  # pragma: no cover - runtime only
        print("Failed to open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = run_inference(frame_rgb, CONFIG)
        detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
        transformed = transform_points(detections, H) if detections else []

        goal_point = (1100, 900)

        pose = get_robot_pose(frame)
        if pose and transformed:
            (cx, cy), _ = pose
            closest = min(
                transformed,
                key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2,
            )
            #TODO: Implement postion for VIP ball collection
            for i in range(6):
                collect_VIP_ball(
                    (cx, cy), 
                    closest, 
                    iterations=i
            )
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = run_inference(frame_rgb, CONFIG)
        detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
        transformed = transform_points(detections, H) if detections else []
            
        pose = get_robot_pose(frame)
        if pose and transformed:
            (cx, cy), _ = pose
            for i in range(8):
                robot_move_to_goal(
                    (cx, cy), 
                    goal_point, 
                    iterations=i
                )
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = run_inference(frame_rgb, CONFIG)
        detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
        transformed = transform_points(detections, H) if detections else []
            

        for i in range(5):
            pose = get_robot_pose(frame)
            if pose and transformed:
                (cx, cy), _ = pose
                closest = min(
                    transformed,
                    key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2,
                )
                for j in range(6):
                    repeat_collection(
                        (cx, cy), 
                        closest, 
                        inner_iteration=j, 
                        outer_iteration=i
                    )
                print("Collection attempted.")
                time.sleep(1)
        
        pose = get_robot_pose(frame)
        if pose and transformed:
            (cx, cy), _ = pose
            for i in range(8):
                robot_move_to_goal(
                    (cx, cy), 
                    goal_point, 
                    iterations=i
                )

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = run_inference(frame_rgb, CONFIG)
        detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
        transformed = transform_points(detections, H) if detections else []
            

        for i in range(5):
            pose = get_robot_pose(frame)
            if pose and transformed:
                (cx, cy), _ = pose
                closest = min(
                    transformed,
                    key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2,
                )
                for j in range(6):
                    repeat_collection(
                        (cx, cy), 
                        closest, 
                        inner_iteration=j, 
                        outer_iteration=i
                    )
                print("Collection attempted.")
                time.sleep(1)
        
        pose = get_robot_pose(frame)
        if pose and transformed:
            (cx, cy), _ = pose
            for i in range(8):
                robot_move_to_goal(
                    (cx, cy), 
                    goal_point, 
                    iterations=i
                )

        


                
        frame_disp = draw_points(frame, detections)
        cv2.imshow("Integrated", frame_disp)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
