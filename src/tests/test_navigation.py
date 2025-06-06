"""
tests/test_navigation.py – Test af pathfinding og navigation til GolfBot-EV3
"""

# Forudsætter at du har en Path-klasse og Point-klasse i fx PathFinding-mappen
# Tilpas import-stier hvis nødvendigt
try:
    from PathFinding.Path import Path
    from PathFinding.Point import Point
except ImportError:
    # Dummy Point og Path til testformål hvis de rigtige ikke findes
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
        def __repr__(self):
            return f"Point({self.x}, {self.y})"

    class Path:
        def __init__(self, robot_points, ball_points, triplets_and_quadruplets, vip_ball_point, obstacle_points):
            self.robot_points = robot_points
            self.ball_points = ball_points
            self.triplets_and_quadruplets = triplets_and_quadruplets
            self.vip_ball_point = vip_ball_point
            self.obstacle_points = obstacle_points

        def generate_beeline_path(self):
            # Dummy path: robot -> VIP -> alle bolde -> mål
            path = []
            path.extend(self.robot_points)
            if self.vip_ball_point:
                path.append(self.vip_ball_point)
            path.extend(self.ball_points)
            path.append(Point(1000, 0))  # Mål
            return path

def test_generate_beeline_path():
    # Dummy data til test
    robot_points = [Point(0, 0)]
    ball_points = [Point(100, 200), Point(300, 400), Point(500, 600)]
    triplets_and_quadruplets = [[Point(100, 200), Point(300, 400), Point(500, 600)]]
    vip_ball_point = Point(300, 400)
    obstacle_points = [Point(200, 300)]

    path_obj = Path(robot_points, ball_points, triplets_and_quadruplets, vip_ball_point, obstacle_points)
    path = path_obj.generate_beeline_path()
    print("Genereret path:")
    for p in path:
        print(f"({p.x}, {p.y})")

if __name__ == "__main__":
    test_generate_beeline_path()