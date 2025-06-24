from cdio_utils import (
    InferenceConfig,
    load_image,
    run_inference,
    transform_points,
    warp_image,
    draw_points,
)
import cv2
import numpy as np
import os
import time
from pathlib import Path
from ImageRecognition.Homography import load_homography
from track_robot_v2 import get_robot_pose
import datetime

# Example usage
API_KEY = "BdmadiDKNX7YzP4unsUm"
TRANSFORM_W, TRANSFORM_H = 1800, 1200
OUTPUT_DIR = "transformed_images"
HOMOGRAPHY_FILE = "./src/homography.npy"
TARGET_FPS = 10  # Process 5 frames per second

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

config = InferenceConfig(
    api_url="http://localhost:9001",
    api_key=API_KEY,
    model_id="tabletennis-ball-detection/1",
)
# Load existing homography matrix
try:
    H = load_homography(HOMOGRAPHY_FILE)
except Exception as e:
    print(f"Error loading homography: {e}")
    exit(1)

# Initialize video capture, Use iriun.com to get the camera working.
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

frame_count = 0
last_frame_time = time.time()
frame_interval = 1.0 / TARGET_FPS
last_saved_time = time.time()
save_interval = 1.0  # seconds
save_count = 0

while True:
    # Calculate time since last frame
    current_time = time.time()
    elapsed = current_time - last_frame_time
    
    # Skip frame if not enough time has passed
    if elapsed < frame_interval:
        time.sleep(0.001)  # Small sleep to prevent CPU hogging
        continue
    
    ret, frame = cap.read()
    if not ret:
        break

    # Update last frame time
    last_frame_time = current_time

    # Save a frame every second
    if current_time - last_saved_time >= save_interval:
        save_path = os.path.join(OUTPUT_DIR, f"source_frame_{save_count:04d}.jpg")
        cv2.imwrite(save_path, frame)
        save_count += 1
        last_saved_time = current_time

    # Convert frame to RGB for processing
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process frame: run inference, transform detections, and draw
    result = run_inference(frame_rgb, config)
    print(result)
    detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
    # Draw detections directly on the original frame
    frame_with_balls = draw_points(frame, detections)

    # --- Use get_robot_pose from track_robot_v2 for robot pose ---
    pose = get_robot_pose(frame)
    frame_with_balls = draw_points(frame, detections)
    if pose:
        (cx, cy), heading = pose
        cv2.circle(frame_with_balls, (int(cx), int(cy)), 5, (0,255,255), -1)
        cv2.putText(frame_with_balls, f"{heading:+6.1f} deg",
                    (int(cx)+10, int(cy)-10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255,255,255), 1)
    # Show the frame in a window
    cv2.imshow("Detected Balls & Robot - Live Feed", frame_with_balls)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
