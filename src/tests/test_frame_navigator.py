import sys
import sys
sys.path.append("src")
from Movement.frame_navigator import calculate_next_command


def test_turn_needed():
    cmd = calculate_next_command((0, 0), 0, (0, 100), angle_threshold=5)
    assert cmd.startswith("turn_right_deg") or cmd.startswith("turn_left_deg")


def test_drive_forward():
    cmd = calculate_next_command((0, 0), 0, (100, 0), angle_threshold=5, capture_distance=10, step_mm=30)
    assert cmd.startswith("drive_straight_mm")


def test_capture_command():
    cmd = calculate_next_command((0, 0), 0, (1, 0), capture_distance=5)
    assert cmd == "capture"
