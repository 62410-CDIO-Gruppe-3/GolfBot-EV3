from src.PathFinding.CartesianCoordinateSystem import CartesianCoordinateSystem
from src.PathFinding.Point import Point


class Obstacle:
    def __init__(self, points):
        self.points = points

    def place_all_in_system(self, coordinate_system):
        for point in self.points:
            point.place_in_system(coordinate_system)
            print(f"Placed point at: {coordinate_system.get_coordinate()}")


# Example usage
coordinate_system = CartesianCoordinateSystem(1800, 1200)
points = [Point(100, 200), Point(300, 400), Point(500, 600)]
obstacle = Obstacle(points)
obstacle.place_all_in_system(coordinate_system)