from src.PathFinding.CartesianCoordinateSystem import CartesianCoordinateSystem
from src.PathFinding.Point import Point


class Ball:
    def __init__(self, point):
        self.point = point

    def place_in_system(self, coordinate_system):
        self.point.place_in_system(coordinate_system)
        print(f"Placed ball at: {coordinate_system.get_coordinate()}")


# Example usage
coordinate_system = CartesianCoordinateSystem(1800, 1200)
point = Point(100, 200)
ball = Ball(point)
ball.place_in_system(coordinate_system)