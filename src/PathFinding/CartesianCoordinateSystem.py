class CartesianCoordinateSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._x = 0
        self._y = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if 0 <= value <= self.width:
            self._x = value
        else:
            raise ValueError(f"x coordinate must be between 0 and {self.width}")

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if 0 <= value <= self.height:
            self._y = value
        else:
            raise ValueError(f"y coordinate must be between 0 and {self.height}")

    def get_coordinate(self):
        return (self._x, self._y)

# Example usage
coordinate_system = CartesianCoordinateSystem(1800, 1200)
coordinate_system.x = 900
coordinate_system.y = 600
print(f"Coordinate: {coordinate_system.get_coordinate()}")