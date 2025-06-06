#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

# Initialize the EV3 brick and MediumMotor on port A
ev3 = EV3Brick()
motor = Motor(Port.A)

def control_gate():
    # Open the gate by rotating forward (30-40 degrees)
    motor.run_angle(150, 35, then=Stop.BRAKE, wait=True)  # Adjust speed and angle as needed

    # Wait for 1.5 seconds
    wait(1500)

    # Close the gate by rotating backward
    motor.run_angle(150, -35, then=Stop.BRAKE, wait=True)  # Reverse with the same angle

# Activate the gate control function
if __name__ == "__main__":
    control_gate()