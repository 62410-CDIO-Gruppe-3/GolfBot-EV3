from __future__ import annotations

import sys
import os
import time

sys.path.append(os.path.parent[0])  # Adjust path to include the src directory
from Movement.AutonomousClient import collect_VIP_ball, repeat_collection, robot_move_to_goal
from ImageRecognition.ImagePoints import get_closest_path_point

def main():
    reference_point = (0, 0)  # This should be the detected arrow tip
    robot_angle = 0.0  # This should be the robot's current angle
    goal_point = (100, 200) 
    tip = reference_point
    destination_points = [(100.01, 200.01), (150.01, 250.01), (200.01, 300.01), (600.01, 200.01), (300.01, 400.01), (1000.01, 800.01), 
                          (700.01, 700.01), (200.01,300.01), (400.01, 200.01), (800.01, 1200.01), (1500.01, 300.01)]  # Example points

    tip = reference_point
    closest_point = get_closest_path_point(destination_points, tip)

    # Collect VIP ball
    collect_VIP_ball(
        tip,
        destination_points,
        robot_angle=robot_angle,
        iterations=6
    )

    next_tip = closest_point 
    tip = next_tip 
    destination_points.remove(closest_point)

    time.sleep(2)  # Wait for a second before next action
    print("Updated tip for next actions:", tip)
    time.sleep(2)

    print("AutonomousClient: Updated list of destinations: ", destination_points, 
          "\n Length of destination points: ", len(destination_points),
            "\n Former closest point:", next_tip)
    
    time.sleep(2)  # Wait for a second before next action

    # Move to goal
    robot_move_to_goal(
        tip,
        goal_point=goal_point,
        robot_angle=robot_angle,
        iterations=8
    )

    next_tip = goal_point
    tip = next_tip
    print("Next tip (goal point):", next_tip)

    time.sleep(2)
    
    # Collect regular balls
    repeat_collection(
        tip, 
        destination_points,
        robot_angle=robot_angle, 
        inner_iteration=6, 
        outer_iteration=5
    )    

    # Move to goal again
    robot_move_to_goal(
        tip,
        goal_point=goal_point,
        robot_angle=robot_angle,
        iterations=8
    )

    next_tip = goal_point
    tip = next_tip
    print("Next tip (goal point):", next_tip)

    time.sleep(2)

    # Collect regular balls again
    repeat_collection(
        tip, 
        destination_points,
        robot_angle=robot_angle, 
        inner_iteration=6, 
        outer_iteration=5
    )

    time.sleep(2)     
    
    # Move to goal again
    robot_move_to_goal(
        tip,
        goal_point=goal_point,
        robot_angle=robot_angle,
        iterations=8
    )

    next_tip = goal_point
    tip = next_tip
    print("Next tip (goal point):", next_tip)

    time.sleep(2)
    exit (0)  # Exit the program
    
if __name__ == "__main__":
    main()