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
from shared_queue import transformed_queue

# Example usage
API_KEY = "BdmadiDKNX7YzP4unsUm"
TRANSFORM_W, TRANSFORM_H = 1200, 1800
OUTPUT_DIR = "transformed_images"
HOMOGRAPHY_FILE = "homography.npy"
TARGET_FPS = 1  # Process 5 frames per second

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

frame_count = 0
last_frame_time = time.time()
frame_interval = 1.0 / TARGET_FPS

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

    # Convert frame to RGB for processing
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process frame: run inference, transform detections, warp, and draw
    result = run_inference(frame_rgb, config)
    detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
    transformed = transform_points(detections, H) if detections else []
    # warped = warp_image(frame_rgb, H, TRANSFORM_W, TRANSFORM_H)
    # warped_out = draw_points(warped, transformed)
    
    # # Convert back to BGR for saving
    # warped_out_bgr = cv2.cvtColor(warped_out, cv2.COLOR_RGB2BGR)
    
    transformed_queue.put(transformed)

    # # Save the transformed frame
    # output_path = os.path.join(OUTPUT_DIR, f"frame_{frame_count:04d}.jpg")
    # cv2.imwrite(output_path, warped_out_bgr)
    
    frame_count += 1

def get_latest_transformed():
    latest = None
    while not transformed_queue.empty():
        latest = transformed_queue.get()
    return latest

# Release resources
cap.release()
cv2.destroyAllWindows()
