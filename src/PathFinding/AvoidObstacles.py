import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Obstacle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

def distance(p1, p2):
    # find distance by using the euclidean distance formula
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def is_too_close(point, obstacles):
    for obs in obstacles:
        # finder nuværende punkt til midten af obstaklet
        dist = distance(point, Point(obs.x, obs.y))
        # indenfor radius + 50 for at undgå de rammer hinanden. 
        # de 50 er bare en ekstra safety margin. Return true hvis tæt på obstacle.
        if dist < obs.radius + 50: 
            return True 
    return False



# Find a path from start to goal avoiding obstacles.
def find_path(start, goal, obstacles):
    path = [start]

    steps = 20
    for i in range(1, steps): # 20 small steps
        t = i / steps

        # a point between start and goal using linear interpolation
        x = (1 - t) * start.x + t * goal.x
        y = (1 - t) * start.y + t * goal.y

        # create a point with the interpolated coordinates
        point = Point(x, y)


        # check if the point is too close to any obstacle
        if is_too_close(point, obstacles):

            # Direction from start to goal.
            dx = goal.x - start.x
            dy = goal.y - start.y
            
            length = math.sqrt(dx**2 + dy**2)
            if length == 0:
                break

            # make detour to avoid the obstacle
            offset_x = -dy / length * 100  
            offset_y = dx / length * 100
            detour = Point(point.x + offset_x, point.y + offset_y)


            path.append(detour)
            break

    path.append(goal)
    return path


if __name__ == "__main__":
    start = Point(100, 100)
    goal = Point(1000, 1000)
    obstacles = [Obstacle(500, 500, 100)]

    path = find_path(start, goal, obstacles)
    for i, p in enumerate(path):
        print(f"Waypoint {i}: ({p.x:.1f}, {p.y:.1f})")


