from src.PathFinding.CartesianCoordinateSystem import CartesianCoordinateSystem


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def place_in_system(self, coordinate_system):
        coordinate_system.x = self.x
        coordinate_system.y = self.y


# Example usage
coordinate_system = CartesianCoordinateSystem(1800, 1200)
point = Point(900, 600)
point.place_in_system(coordinate_system)
print(f"Coordinate: {coordinate_system.get_coordinate()}")