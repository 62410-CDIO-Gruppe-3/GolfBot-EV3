import sys
sys.path.append(r"C:\\Users\\hatal\\GolfBot-EV3\\src")

import math

class ArrowVector:
    def __init__(self, point_a: tuple[int, int], point_b: tuple[int, int]):
        """
        Initialize with two points defining the arrow vector.
        
        Args:
            point_a: The starting point (x, y).
            point_b: The ending point (x, y).
        """
        self.point_a = point_a
        self.point_b = point_b
        self._vector = (point_b[0] - point_a[0], point_b[1] - point_a[1])
    
    def get_x(self) -> int:
        """Return the horizontal component of the vector."""
        return self._vector[0]

    def get_y(self) -> int:
        """Return the vertical component of the vector."""
        return self._vector[1]

    def get_angle(self) -> float:
        """Return the angle (in degrees) of the vector."""
        return math.degrees(math.atan2(self._vector[1], self._vector[0]))

    def get_size(self) -> float:
        """Return the magnitude (length) of the vector."""
        return math.hypot(self._vector[0], self._vector[1])