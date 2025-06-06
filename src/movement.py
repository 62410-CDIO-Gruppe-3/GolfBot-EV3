"""
movement.py – Bevægelsesfunktioner til GolfBot-EV3
Abstraherer robotkørsel vha. DriveBase.
"""

from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop
from pybricks.robotics import DriveBase
from config import (
    PORT_LEFT_MOTOR,
    PORT_RIGHT_MOTOR,
    WHEEL_DIAMETER_MM,
    AXLE_TRACK_MM,
    DRIVE_SPEED,
    TURN_SPEED,
)
from utils import debug_log

# Initialiser motorer og DriveBase
motor_left = Motor(Port[PORT_LEFT_MOTOR])
motor_right = Motor(Port[PORT_RIGHT_MOTOR])
drivebase = DriveBase(
    motor_left,
    motor_right,
    wheel_diameter=WHEEL_DIAMETER_MM,
    axle_track=AXLE_TRACK_MM,
)

def drive_forward(distance_mm, speed=DRIVE_SPEED):
    """Kør fremad en given distance i mm."""
    debug_log(f"Kører frem: {distance_mm} mm med hastighed {speed}")
    drivebase.straight(distance_mm)

def turn_left(angle_deg, speed=TURN_SPEED):
    """Drej til venstre med en given vinkel i grader."""
    debug_log(f"Drejer venstre: {angle_deg} grader med hastighed {speed}")
    drivebase.turn(-abs(angle_deg))

def turn_right(angle_deg, speed=TURN_SPEED):
    """Drej til højre med en given vinkel i grader."""
    debug_log(f"Drejer højre: {angle_deg} grader med hastighed {speed}")
    drivebase.turn(abs(angle_deg))

def stop_motors():
    """Stopper begge hjulmotorer med bremse."""
    debug_log("Stopper hjulmotorer.")
    motor_left.stop()
    motor_right.stop()