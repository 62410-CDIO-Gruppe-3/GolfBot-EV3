from pathlib import Path
import sys
import cv2
import numpy as np
import time
import os

# Allow imports from the src directory
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
SRC = ROOT / "src"

from cdio_utils import (
    InferenceConfig,
    run_inference,
    transform_points,
    draw_points,
)
from ImageRecognition.Homography import load_homography
from test_robot_v2 import get_robot_pose
from Movement.AutonomousClient import send_and_receive
from Movement.CommandLoop import (
    get_command_to_ball,
    get_ball_collection_sequence,
    get_command_to_goal,
    get_goal_drop_off_sequence,
)
from PathFinding.ArrowVector import ArrowVector

# Constants
API_KEY = "BdmadiDKNX7YzP4unsUm"
TRANSFORM_W, TRANSFORM_H = 1800, 1200
HOMOGRAPHY_FILE = SRC / "homography.npy"
TARGET_FPS = 3  # Process 10 frames per second

# Inference Config
CONFIG = InferenceConfig(
    api_url="http://localhost:9001",
    api_key=API_KEY,
    model_id="tabletennis-ball-detection/1",
)

def find_closest_ball(robot_pos, ball_positions):
    if not ball_positions.any():
        return None
    closest_ball = min(
        ball_positions,
        key=lambda ball_pos: np.linalg.norm(np.array(robot_pos) - np.array(ball_pos)),
    )
    return closest_ball

def main() -> None:
    try:
        H = load_homography(HOMOGRAPHY_FILE)
    except Exception as exc:
        print(f"Could not load homography: {exc}")
        return

    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened():
        print("Failed to open camera")
        return

    # State machine variables
    robot_state = "SEARCHING_BALL"  # States: SEARCHING_BALL, MOVING_TO_BALL, COLLECTING_BALL, MOVING_TO_GOAL, DROPPING_BALL
    target_ball = None
    goal_position = (TRANSFORM_W // 2, 50)  # Adjust as needed

    # Ball tracking grace period variables
    last_ball_seen_time = None
    last_known_ball_position = None
    BALL_GRACE_PERIOD = 15.0  # seconds

    # Oscillation prevention variables
    last_turns = []  # List of (direction, magnitude)
    MIN_TURN_ANGLE = 5.0

    last_frame_time = time.time()
    frame_interval = 1.0 / TARGET_FPS

    while True:
        current_time = time.time()
        elapsed = current_time - last_frame_time

        if elapsed < frame_interval:
            time.sleep(0.001)
            continue
        
        last_frame_time = current_time

        ret, frame = cap.read()
        if not ret:
            break

        # --- Vision Processing ---
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = run_inference(frame_rgb, CONFIG)
        detections = [(p["x"], p["y"]) for p in result.get("predictions", [])]
        
        transformed_balls = transform_points(detections, H)
        pose = get_robot_pose(frame)
        
        # --- Robot Control Logic ---
        if pose:
            robot_center_orig, robot_heading = pose
            # Calculate robot tip in original frame
            robot_tip_orig = (
                robot_center_orig[0] + 30 * np.cos(np.deg2rad(robot_heading)),
                robot_center_orig[1] + 30 * np.sin(np.deg2rad(robot_heading)),
            )
            
            # Transform robot points to warped perspective
            robot_points_transformed = transform_points([robot_center_orig, robot_tip_orig], H)
            if len(robot_points_transformed) == 2:
                robot_center, robot_tip = robot_points_transformed
                
                # Recalculate heading in transformed space for accurate angle calculations
                robot_heading_transformed = ArrowVector(robot_center, robot_tip).get_angle()

                if robot_state == "SEARCHING_BALL":
                    target_ball = find_closest_ball(robot_center, transformed_balls)
                    if target_ball is not None:
                        print(f"New target ball found at {target_ball}")
                        last_ball_seen_time = current_time
                        last_known_ball_position = target_ball
                        robot_state = "MOVING_TO_BALL"
                    else:
                        print("No balls found, searching...")

                elif robot_state == "MOVING_TO_BALL":
                    if target_ball is not None:
                        # Check if the target ball is still visible
                        visible = any(np.linalg.norm(np.array(target_ball) - np.array(b)) < 20 for b in transformed_balls)
                        if visible:
                            last_ball_seen_time = current_time
                            last_known_ball_position = target_ball
                        else:
                            # Ball not visible, check grace period
                            if last_ball_seen_time is not None and (current_time - last_ball_seen_time) < BALL_GRACE_PERIOD:
                                print(f"Target ball lost, but within grace period ({current_time - last_ball_seen_time:.1f}s). Continuing to last known position.")
                                target_ball = last_known_ball_position
                            else:
                                print("Target ball lost for over 15 seconds. Returning to search.")
                                robot_state = "SEARCHING_BALL"
                                target_ball = None
                                last_known_ball_position = None
                                last_ball_seen_time = None
                                last_turns.clear()  # Reset turn tracking
                                continue

                        command = get_command_to_ball(robot_tip, target_ball, robot_heading_transformed)
                        # Oscillation prevention for turn commands
                        if command and (command.strip().startswith("turn_left_deg") or command.strip().startswith("turn_right_deg")):
                            # Parse direction and angle
                            if command.strip().startswith("turn_left_deg"):
                                direction = "left"
                            else:
                                direction = "right"
                            try:
                                angle = float(command.strip().split("(")[1].split(")")[0])
                            except Exception:
                                angle = None
                            # Check for oscillation
                            if len(last_turns) >= 2:
                                prev_dir, prev_angle = last_turns[-1]
                                prev2_dir, prev2_angle = last_turns[-2]
                                if (
                                    prev_dir != prev2_dir and
                                    prev_angle == prev2_angle and
                                    direction != prev_dir and
                                    angle == prev_angle
                                ):
                                    # Oscillation detected, halve the angle
                                    new_angle = max(angle / 2, MIN_TURN_ANGLE)
                                    print(f"Oscillation detected. Reducing turn angle to {new_angle}.")
                                    command = f"turn_{direction}_deg({new_angle:.2f})\n"
                                    angle = new_angle
                            last_turns.append((direction, angle))
                            if len(last_turns) > 2:
                                last_turns = last_turns[-2:]
                        else:
                            last_turns.clear()  # Reset on non-turn command
                        if command:
                            response = send_and_receive(command)
                            print("Response from EV3:", response)
                            # If the command is a turn, wait a few seconds before next command
                            if command.strip().startswith("turn_left_deg") or command.strip().startswith("turn_right_deg"):
                                print("Turn command issued. Waiting for robot to finish turning...")
                                time.sleep(2)  # Wait 2 seconds (adjust as needed)
                                # After waiting, skip sending another command this frame
                                continue
                        else:
                            print("Arrived at the ball. Starting collection sequence.")
                            robot_state = "COLLECTING_BALL"
                            last_turns.clear()
                    else:
                        robot_state = "SEARCHING_BALL"
                        last_turns.clear()

                elif robot_state == "COLLECTING_BALL":
                    sequence = get_ball_collection_sequence()
                    for command in sequence:
                        response = send_and_receive(command)
                        print("Response from EV3:", response)
                        time.sleep(1) # Give time for action to complete
                    print("Ball collected.")
                    target_ball = None
                    last_turns.clear()
                    if find_closest_ball(robot_center, transformed_balls) is None:
                        robot_state = "MOVING_TO_GOAL"
                    else:
                        robot_state = "SEARCHING_BALL"

                elif robot_state == "MOVING_TO_GOAL":
                    command = get_command_to_goal(robot_tip, goal_position, robot_heading_transformed)
                    # Oscillation prevention for turn commands
                    if command and (command.strip().startswith("turn_left_deg") or command.strip().startswith("turn_right_deg")):
                        if command.strip().startswith("turn_left_deg"):
                            direction = "left"
                        else:
                            direction = "right"
                        try:
                            angle = float(command.strip().split("(")[1].split(")")[0])
                        except Exception:
                            angle = None
                        if len(last_turns) >= 2:
                            prev_dir, prev_angle = last_turns[-1]
                            prev2_dir, prev2_angle = last_turns[-2]
                            if (
                                prev_dir != prev2_dir and
                                prev_angle == prev2_angle and
                                direction != prev_dir and
                                angle == prev_angle
                            ):
                                new_angle = max(angle / 2, MIN_TURN_ANGLE)
                                print(f"Oscillation detected. Reducing turn angle to {new_angle}.")
                                command = f"turn_{direction}_deg({new_angle:.2f})\n"
                                angle = new_angle
                        last_turns.append((direction, angle))
                        if len(last_turns) > 2:
                            last_turns = last_turns[-2:]
                    else:
                        last_turns.clear()
                    if command:
                        response = send_and_receive(command)
                        print("Response from EV3:", response)
                        if command.strip().startswith("turn_left_deg") or command.strip().startswith("turn_right_deg"):
                            print("Turn command issued. Waiting for robot to finish turning...")
                            time.sleep(2)
                            continue
                    else:
                        print("Arrived at the goal. Starting drop-off sequence.")
                        robot_state = "DROPPING_BALL"
                        last_turns.clear()
                
                elif robot_state == "DROPPING_BALL":
                    sequence = get_goal_drop_off_sequence()
                    for command in sequence:
                        response = send_and_receive(command)
                        print("Response from EV3:", response)
                        time.sleep(1) # Give time for action to complete
                    print("Ball drop-off complete.")
                    robot_state = "SEARCHING_BALL"

        # --- Visualization ---
        frame_disp = draw_points(frame, detections)
        if pose:
            (cx, cy), heading = pose
            cv2.circle(frame_disp, (int(cx), int(cy)), 5, (0, 255, 255), -1)
            cv2.putText(
                frame_disp,
                f"{heading:+6.1f} deg | State: {robot_state}",
                (int(cx) + 10, int(cy) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
        # Resize for preview window only
        preview_disp = cv2.resize(frame_disp, (480, 270))
        cv2.imshow("Integrated Program", preview_disp)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
