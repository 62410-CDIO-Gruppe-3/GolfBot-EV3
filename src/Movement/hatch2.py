#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

# Initialize the EV3 brick and Motor_PUSH on port B
ev3 = EV3Brick()
Motor_PUSH = Motor(Port.B)

def PushOutBalls():
    # Push balls forward (approximately 40 degrees)
    Motor_PUSH.run_target(500, 40, then=Stop.BRAKE, wait=True)  # Fast forward motion

    # Wait for 0.5 seconds
    wait(500)

    # Return the motor to the starting position
    Motor_PUSH.run_target(500, 0, then=Stop.BRAKE, wait=True)  # Reverse to start position

# Example usage
if __name__ == "__main__":
    PushOutBalls()