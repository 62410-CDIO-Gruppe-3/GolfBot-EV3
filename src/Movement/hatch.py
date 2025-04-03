from ev3dev2.motor import MediumMotor, OUTPUT_A, SpeedPercent
from time import sleep

# Initialize the MediumMotor on port A
motor = MediumMotor(OUTPUT_A)

def control_gate():
    # Open the gate by rotating forward (30-40 degrees)
    motor.on_for_degrees(SpeedPercent(50), 35)  # Adjust speed and degrees as needed
    motor.stop(brake=True)  # Brake after movement

    # Wait for 1.5 seconds
    sleep(1.5)

    # Close the gate by rotating backward
    motor.on_for_degrees(SpeedPercent(-50), 35)  # Reverse with the same degrees
    motor.stop(brake=True)  # Brake after movement

# Activate the gate control function
if __name__ == "__main__":
    control_gate()