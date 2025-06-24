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
from test_robot_v2 import get_robot_pose
import datetime
from src.Movement.AutonomousClient import send_and_receive
from src.Movement.CommandLoop import (
    get_command_to_ball,
    get_ball_collection_sequence,
    get_command_to_goal,
    get_goal_drop_off_sequence,
)
from src.PathFinding.ArrowVector import ArrowVector

# Example usage
API_KEY = "BdmadiDKNX7YzP4unsUm"
TRANSFORM_W, TRANSFORM_H = 1800, 1200
OUTPUT_DIR = "transformed_images"
HOMOGRAPHY_FILE = "homography.npy"
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

# State machine variables
robot_state = "SEARCHING_BALL"  # Possible states: SEARCHING_BALL, MOVING_TO_BALL, COLLECTING_BALL, MOVING_TO_GOAL, DROPPING_BALL
target_ball = None
last_known_ball = None
blind_approach_start_time = None
BLIND_APPROACH_DURATION = 15.0  # seconds
goal_position = (TRANSFORM_W // 2, 50) # Example goal position, adjust as needed

frame_count = 0
last_frame_time = time.time()
frame_interval = 1.0 / TARGET_FPS
last_saved_time = time.time()
save_interval = 1.0  # seconds
save_count = 0


def find_closest_ball(robot_pos, ball_positions):
    if not ball_positions:
        return None
    closest_ball = min(
        ball_positions,
        key=lambda ball_pos: np.linalg.norm(np.array(robot_pos) - np.array(ball_pos)),
    )
    return closest_ball


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

    # --- Vision Processing ---
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = run_inference(frame_rgb, config)
    detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
    
    transformed_balls = transform_points(detections, H)
    pose = get_robot_pose(frame)

    # --- Robot Control Logic ---
    if pose:
        robot_center_orig, robot_heading = pose
        robot_tip_orig = (
            robot_center_orig[0] + 30 * np.cos(np.deg2rad(robot_heading)),
            robot_center_orig[1] + 30 * np.sin(np.deg2rad(robot_heading)),
        )
        
        # Transform robot points
        robot_points_transformed = transform_points([robot_center_orig, robot_tip_orig], H)
        if len(robot_points_transformed) == 2:
            robot_center, robot_tip = robot_points_transformed
            
            # Recalculate heading in transformed space
            robot_heading_transformed = ArrowVector(robot_center, robot_tip).get_angle()

            if robot_state == "SEARCHING_BALL":
                target_ball = find_closest_ball(robot_center, transformed_balls)
                if target_ball:
                    print(f"New target ball found at {target_ball}")
                    last_known_ball = target_ball
                    robot_state = "MOVING_TO_BALL"
                    blind_approach_start_time = None
                else:
                    print("No balls found, searching...")
                    # Optional: Implement a search pattern, e.g., turn in place
                    # response = send_and_receive("turn_right_deg(30)\n")
                    # print("Response from EV3:", response)

            elif robot_state == "MOVING_TO_BALL":
                if target_ball:
                    # Check if the target ball is still visible
                    if not any(np.linalg.norm(np.array(target_ball) - np.array(b)) < 20 for b in transformed_balls):
                        print("Target ball lost. Initiating blind approach to last known position.")
                        last_known_ball = target_ball
                        target_ball = None
                        blind_approach_start_time = time.time()
                        # Continue to next logic below
                    else:
                        last_known_ball = target_ball
                        blind_approach_start_time = None
                        command = get_command_to_ball(robot_tip, target_ball, robot_heading_transformed)
                        if command:
                            response = send_and_receive(command)
                            print("Response from EV3:", response)
                        else:
                            print("Arrived at the ball. Starting collection sequence.")
                            robot_state = "COLLECTING_BALL"
                        continue
                # If target_ball is None but we have a last_known_ball, do blind approach
                if last_known_ball and blind_approach_start_time is not None:
                    elapsed_blind = time.time() - blind_approach_start_time
                    if elapsed_blind < BLIND_APPROACH_DURATION:
                        print(f"Blindly approaching last known ball position {last_known_ball} ({elapsed_blind:.1f}s elapsed)")
                        command = get_command_to_ball(robot_tip, last_known_ball, robot_heading_transformed)
                        if command:
                            response = send_and_receive(command)
                            print("Response from EV3:", response)
                        else:
                            print("Arrived at the last known ball position. Starting collection sequence.")
                            robot_state = "COLLECTING_BALL"
                            last_known_ball = None
                            blind_approach_start_time = None
                    else:
                        print("Blind approach timed out. Returning to search.")
                        robot_state = "SEARCHING_BALL"
                        last_known_ball = None
                        blind_approach_start_time = None
                else:
                    robot_state = "SEARCHING_BALL"

            elif robot_state == "COLLECTING_BALL":
                sequence = get_ball_collection_sequence()
                for command in sequence:
                    response = send_and_receive(command)
                    print("Response from EV3:", response)
                    time.sleep(1) # Give time for action to complete
                print("Ball collected.")
                target_ball = None
                if find_closest_ball(robot_center, transformed_balls) is None:
                     robot_state = "MOVING_TO_GOAL"
                else:
                     robot_state = "SEARCHING_BALL"


            elif robot_state == "MOVING_TO_GOAL":
                command = get_command_to_goal(robot_tip, goal_position, robot_heading_transformed)
                if command:
                    response = send_and_receive(command)
                    print("Response from EV3:", response)
                else:
                    print("Arrived at the goal. Starting drop-off sequence.")
                    robot_state = "DROPPING_BALL"
            
            elif robot_state == "DROPPING_BALL":
                sequence = get_goal_drop_off_sequence()
                for command in sequence:
                    response = send_and_receive(command)
                    print("Response from EV3:", response)
                    time.sleep(1) # Give time for action to complete
                print("Ball drop-off complete. Task finished or search for more balls.")
                robot_state = "SEARCHING_BALL" # Or an "IDLE" state

    # --- Visualization ---
    frame_with_balls = draw_points(frame, detections)
    # Draw robot pose on original frame
    if pose:
        (cx, cy), heading = pose
        cv2.circle(frame_with_balls, (int(cx), int(cy)), 5, (0, 255, 255), -1)
        cv2.putText(
            frame_with_balls,
            f"{heading:+6.1f} deg | State: {robot_state}",
            (int(cx) + 10, int(cy) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

    # Show the frame in a window
    cv2.imshow("Detected Balls & Robot - Live Feed", frame_with_balls)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
