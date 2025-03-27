from math import sqrt

from src.PathFinding.Point import Point


class Path:
    def __init__(self, robot_points, ball_points, triplets_and_quadruplets, vip_ball_point, obstacle_points):
        self.robot_points = robot_points
        self.ball_points = ball_points
        self.triplets_and_quadruplets = triplets_and_quadruplets
        self.vip_ball_point = vip_ball_point
        self.obstacle_points = obstacle_points

    def place_all_in_system(self, coordinate_system):
        for point in self.robot_points:
            point.place_in_system(coordinate_system)
            print(f"Placed robot point at: {coordinate_system.get_coordinate()}")

        for point in self.ball_points:
            point.place_in_system(coordinate_system)
            print(f"Placed ball point at: {coordinate_system.get_coordinate()}")

        for group in self.triplets_and_quadruplets:
            for point in group:
                point.place_in_system(coordinate_system)
                print(f"Placed triplet/quadruplet point at: {coordinate_system.get_coordinate()}")

        self.vip_ball_point.place_in_system(coordinate_system)
        print(f"Placed VIP ball point at: {coordinate_system.get_coordinate()}")

        for point in self.obstacle_points:
            point.place_in_system(coordinate_system)
            print(f"Placed obstacle point at: {coordinate_system.get_coordinate()}")

    def calculate_distance(self, point1, point2):
        return sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def is_point_in_obstacles(self, point):
        for obstacle_point in self.obstacle_points:
            if point.x == obstacle_point.x and point.y == obstacle_point.y:
                return True
        return False

    def generate_beeline_path(self):
        path = []
        current_point = self.robot_points[0]

        # Generate beeline to the cluster containing the VIP ball
        for group in self.triplets_and_quadruplets:
            if self.vip_ball_point in group:
                for point in group:
                    if not self.is_point_in_obstacles(point):
                        path.append(point)
                break

        # Add VIP ball point
        path.append(self.vip_ball_point)

        # Generate beeline to the point (1750, 600)
        final_point = Point(1750, 600)
        if not self.is_point_in_obstacles(final_point):
            path.append(final_point)

        return path