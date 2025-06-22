from __future__ import annotations

from typing import List, Tuple
import cv2

from track_robot import get_robot_pose
from PathFinding.ArrowVector import ArrowVector
from AutonomousClient import send_and_receive


# --- helper ---------------------------------------------------------------

def calculate_next_command(robot_pos: Tuple[int, int], heading_deg: float,
                           target_pos: Tuple[int, int], *,
                           angle_threshold: float = 10.0,
                           capture_distance: float = 80.0,
                           step_mm: float = 80.0) -> str:
    """Return the next command for moving towards *target_pos*.

    The command is one of:
        - "turn_left_deg(... )\n"
        - "turn_right_deg(... )\n"
        - "drive_straight_mm(... )\n"
        - "capture" when the robot should pick up the ball
    """
    vector = ArrowVector(robot_pos, target_pos)
    distance = vector.get_size()
    target_angle = vector.get_angle()

    diff = (target_angle - heading_deg + 360) % 360
    if diff > 180:
        diff -= 360

    if abs(diff) > angle_threshold:
        if diff > 0:
            return f"turn_right_deg({abs(int(diff))})\n"
        return f"turn_left_deg({abs(int(diff))})\n"

    if distance > capture_distance:
        step = min(step_mm, distance - capture_distance)
        return f"drive_straight_mm({int(step)})\n"

    return "capture"


# --- main navigation class -----------------------------------------------

class FrameNavigator:
    def __init__(self, balls: List[Tuple[int, int]], *,
                 angle_threshold: float = 10.0,
                 capture_distance: float = 80.0,
                 step_mm: float = 80.0,
                 video_src: int = 0):
        self.balls = list(balls)
        self.angle_threshold = angle_threshold
        self.capture_distance = capture_distance
        self.step_mm = step_mm
        self.cap = cv2.VideoCapture(video_src)

    def close(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None

    def run(self) -> None:
        idx = 0
        while idx < len(self.balls) and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            pose = get_robot_pose(frame)
            if not pose:
                continue
            (cx, cy), heading = pose
            cmd = calculate_next_command((cx, cy), heading, self.balls[idx],
                                         angle_threshold=self.angle_threshold,
                                         capture_distance=self.capture_distance,
                                         step_mm=self.step_mm)
            if cmd == "capture":
                capture_seq = (
                    "open_gate()\n"
                    "drive_straight_mm(50)\n"
                    "close_gate()\n"
                )
                send_and_receive(capture_seq)
                idx += 1
            else:
                send_and_receive(cmd)
        self.close()

