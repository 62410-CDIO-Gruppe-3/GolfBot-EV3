"""
tests/test_integration.py – End-to-end/integrationstest for GolfBot-EV3
Simulerer hele flowet: find bold → planlæg rute → kør → saml bold → aflever bold.
"""

import sys
import types
from config import BALL_COUNT_MAX
from utils import debug_log

# Mockede hardware-funktioner
def mock_open_gate(motor): debug_log("MOCK: open_gate called")
def mock_close_gate(motor): debug_log("MOCK: close_gate called")
def mock_push_balls(motor): debug_log("MOCK: push_balls called")
def mock_stop_all_motors(*motors): debug_log("MOCK: stop_all_motors called")
def mock_drive_forward(distance): debug_log(f"MOCK: drive_forward({distance}) called")

# Patch utils og movement
import utils, movement
utils.open_gate = mock_open_gate
utils.close_gate = mock_close_gate
utils.push_balls = mock_push_balls
utils.stop_all_motors = mock_stop_all_motors
movement.drive_forward = mock_drive_forward

from vision import BallDetector
try:
    from PathFinding.Path import Path
    from PathFinding.Point import Point
except ImportError:
    class Point:
        def __init__(self, x, y): self.x = x; self.y = y
    class Path:
        def __init__(self, robot_points, ball_points, triplets_and_quadruplets, vip_ball_point, obstacle_points):
            self.robot_points = robot_points
            self.ball_points = ball_points
            self.triplets_and_quadruplets = triplets_and_quadruplets
            self.vip_ball_point = vip_ball_point
            self.obstacle_points = obstacle_points
        def generate_beeline_path(self):
            path = []
            path.extend(self.robot_points)
            if self.vip_ball_point: path.append(self.vip_ball_point)
            path.extend(self.ball_points)
            path.append(Point(1000, 0))
            return path

def simulate_integration_flow():
    debug_log("Starter integrationstest for GolfBot-EV3...")

    # 1. Find bolde (simuleret med vision)
    detector = BallDetector()
    import cv2
    test_image = "assets/test_image0.jpg"
    frame = cv2.imread(test_image)
    balls = detector.detect_balls(frame)
    vip = detector.detect_vip(frame)
    debug_log(f"Fundne bolde: {balls}")
    debug_log(f"VIP-bold: {vip}")
    assert balls is not None, "Vision returnerede ingen bolde-liste"
    assert isinstance(balls, list), "Vision returnerede ikke en liste"
    assert len(balls) > 0, "Ingen bolde fundet i testbillede"

    # 2. Planlæg rute (simuleret)
    robot_start = [Point(0, 0)]
    ball_points = [Point(x, y) for (x, y) in balls]
    vip_point = Point(*vip) if vip else None
    triplets_and_quadruplets = [ball_points]
    obstacle_points = []

    path_obj = Path(robot_start, ball_points, triplets_and_quadruplets, vip_point, obstacle_points)
    path = path_obj.generate_beeline_path()
    debug_log(f"Planlagt path: {[ (p.x, p.y) for p in path ]}")
    assert len(path) >= 2, "Path for kort"

    # 3. Kør ruten (mock)
    for idx, point in enumerate(path):
        debug_log(f"Kører til punkt {idx+1}: ({point.x}, {point.y})")
        movement.drive_forward(200)

    # 4. Saml bold (mock)
    utils.open_gate("motor_gate")
    utils.close_gate("motor_gate")
    debug_log("Bold opsamlet.")

    # 5. Aflever bolde (mock)
    for i in range(BALL_COUNT_MAX):
        utils.push_balls("motor_push")
        debug_log(f"Bold {i+1} afleveret.")

    utils.stop_all_motors("motor_left", "motor_right", "motor_gate", "motor_push")
    debug_log("Integrationstest afsluttet.")

if __name__ == "__main__":
    simulate_integration_flow()