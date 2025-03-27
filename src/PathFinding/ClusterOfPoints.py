from math import sqrt
from itertools import combinations
from src.PathFinding.CartesianCoordinateSystem import CartesianCoordinateSystem
from src.PathFinding.Point import Point


class ClusterOfPoints:
    def __init__(self, points):
        self.points = points

    def place_all_in_system(self, coordinate_system):
        for point in self.points:
            point.place_in_system(coordinate_system)
            print(f"Placed point at: {coordinate_system.get_coordinate()}")

    def calculate_distance(self, point1, point2):
        return sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def generate_triplets_and_quadruplets(self):
        triplets_and_quadruplets = []
        points = self.points[:]

        while len(points) >= 3:
            if len(points) == 4:
                triplets_and_quadruplets.append(points)
                break

            # Find the closest triplet
            min_distance = float('inf')
            best_triplet = None
            for triplet in combinations(points, 3):
                distance = (self.calculate_distance(triplet[0], triplet[1]) +
                            self.calculate_distance(triplet[1], triplet[2]) +
                            self.calculate_distance(triplet[2], triplet[0]))
                if distance < min_distance:
                    min_distance = distance
                    best_triplet = triplet

            triplets_and_quadruplets.append(list(best_triplet))
            for point in best_triplet:
                points.remove(point)

        return triplets_and_quadruplets


# Example usage
coordinate_system = CartesianCoordinateSystem(1800, 1200)
points = [Point(100, 200), Point(300, 400), Point(500, 600), Point(700, 800), Point(900, 1000), Point(1100, 1200),
          Point(1300, 1400)]
cluster = ClusterOfPoints(points)
triplets_and_quadruplets = cluster.generate_triplets_and_quadruplets()
for group in triplets_and_quadruplets:
    print([f"({p.x}, {p.y})" for p in group])