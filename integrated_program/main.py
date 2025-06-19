import cv2
import time
from cdio_utils import InferenceConfig, run_inference, transform_points
from ImageRecognition.Homography import load_homography
from ImageRecognition.ArrowDetection import detect_arrow_tip
from Movement.AutonomousClient import repeat_collection

"""Main integration script combining image recognition and movement."""

API_URL = "http://localhost:9001"
API_KEY = "BdmadiDKNX7YzP4unsUm"
MODEL_ID = "tabletennis-ball-detection/1"
HOMOGRAPHY_FILE = "homography.npy"
ARROW_TEMPLATE_PATH = "arrow_template.jpg"  # Provide a grayscale arrow image
TARGET_FPS = 1


def main() -> None:
    config = InferenceConfig(api_url=API_URL, api_key=API_KEY, model_id=MODEL_ID)
    try:
        H = load_homography(HOMOGRAPHY_FILE)
    except Exception as e:
        print(f"Failed to load homography: {e}")
        return

    arrow_template = cv2.imread(ARROW_TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    if arrow_template is None:
        print(f"Arrow template not found: {ARROW_TEMPLATE_PATH}")

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    last = time.time()
    interval = 1.0 / TARGET_FPS
    try:
        while True:
            now = time.time()
            if now - last < interval:
                time.sleep(0.01)
                continue
            last = now

            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = run_inference(frame_rgb, config)
            balls_img = [(p["x"], p["y"]) for p in result.get("predictions", [])]
            ball_points = (
                transform_points(balls_img, H).tolist() if balls_img else []
            )

            robot_tip = None
            if arrow_template is not None:
                robot_tip = detect_arrow_tip(frame, arrow_template)
            if robot_tip is not None:
                robot_tip = transform_points([robot_tip], H)[0].tolist()

            print(f"Robot position: {robot_tip}")
            print(f"Ball positions: {ball_points}")

            if robot_tip and ball_points:
                repeat_collection(robot_tip, ball_points, inner_iteration=6, outer_iteration=1)
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
