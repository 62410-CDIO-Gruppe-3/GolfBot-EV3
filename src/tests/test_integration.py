"""
tests/test_integration.py – End-to-end/integrationstest for GolfBot-EV3
Simulerer hele flowet: find bold → planlæg rute → kør → saml bold → aflever bold.
"""

from config import BALL_COUNT_MAX
from utils import open_gate, close_gate, push_balls, debug_log, stop_all_motors
from movement import drive_forward, turn_left, turn_right, stop_motors
from vision import BallDetector
try:
    from PathFinding.Path import Path
    from PathFinding.Point import Point
except ImportError:
    # Dummy classes hvis PathFinding ikke er tilgængelig
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
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
            if self.vip_ball_point:
                path.append(self.vip_ball_point)
            path.extend(self.ball_points)
            path.append(Point(1000, 0))  # Mål
            return path

def simulate_integration_flow():
    debug_log("Starter integrationstest for GolfBot-EV3...")

    # 1. Find bolde (simuleret med vision)
    detector = BallDetector()
    # Her bruges et testbillede – i praksis ville det være et live frame
    import cv2
    test_image = "test_images/banebillede.jpg"
    frame = cv2.imread(test_image)
    balls = detector.detect_balls(frame)
    vip = detector.detect_vip(frame)
    debug_log(f"Fundne bolde: {balls}")
    debug_log(f"VIP-bold: {vip}")

    # 2. Planlæg rute (simuleret)
    robot_start = [Point(0, 0)]
    ball_points = [Point(x, y) for (x, y) in balls]
    vip_point = Point(*vip) if vip else None
    triplets_and_quadruplets = [ball_points]  # For simplicity
    obstacle_points = []  # Ingen forhindringer i denne test

    path_obj = Path(robot_start, ball_points, triplets_and_quadruplets, vip_point, obstacle_points)
    path = path_obj.generate_beeline_path()
    debug_log(f"Planlagt path: {[ (p.x, p.y) for p in path ]}")

    # 3. Kør ruten (simuleret)
    for idx, point in enumerate(path):
        debug_log(f"Kører til punkt {idx+1}: ({point.x}, {point.y})")
        drive_forward(200)  # Simuleret distance

    # 4. Saml bold (simuleret)
    open_gate("motor_gate")
    close_gate("motor_gate")
    debug_log("Bold opsamlet.")

    # 5. Aflever bolde (simuleret)
    for i in range(BALL_COUNT_MAX):
        push_balls("motor_push")
        debug_log(f"Bold {i+1} afleveret.")

    stop_all_motors("motor_left", "motor_right", "motor_gate", "motor_push")
    debug_log("Integrationstest afsluttet.")

if __name__ == "__main__":
    simulate_integration_flow()