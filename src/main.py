#!/usr/bin/env pybricks-micropython
"""
main.py – Hovedprogram for GolfBot-EV3
Styrer hele robotflowet: kørsel, portstyring, boldopsamling og aflevering.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, TouchSensor, UltrasonicSensor, GyroSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

from config import (
    PORT_LEFT_MOTOR,
    PORT_RIGHT_MOTOR,
    PORT_GATE_MOTOR,
    PORT_PUSH_MOTOR,
    PORT_COLOR_SENSOR,
    PORT_TOUCH_SENSOR,
    PORT_ULTRASONIC_SENSOR,
    PORT_GYRO_SENSOR,
    DRIVE_SPEED,
    BALL_COUNT_MAX,
    WHEEL_DIAMETER_MM,
    AXLE_TRACK_MM,
)
from utils import open_gate, close_gate, push_balls, stop_all_motors, debug_log

# --- Initialisering af hardware ---
ev3 = EV3Brick()

motor_left = Motor(Port[PORT_LEFT_MOTOR])
motor_right = Motor(Port[PORT_RIGHT_MOTOR])
motor_gate = Motor(Port[PORT_GATE_MOTOR])
motor_push = Motor(Port[PORT_PUSH_MOTOR])

sensor_color = ColorSensor(Port[PORT_COLOR_SENSOR])
sensor_touch = TouchSensor(Port[PORT_TOUCH_SENSOR])
sensor_ultra = UltrasonicSensor(Port[PORT_ULTRASONIC_SENSOR])
sensor_gyro = GyroSensor(Port[PORT_GYRO_SENSOR])

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

def collect_ball():
    """Åbn port, vent, luk port – simulerer boldopsamling."""
    open_gate(motor_gate)
    wait(300)
    close_gate(motor_gate)

def go_to_goal():
    """Kør til målzonen (dummy-funktion – kan udvides med navigation/vision)."""
    debug_log("Kører til målzonen...")
    drive_forward(1000)  # Justér distance efter bane

def deliver_balls(ball_count):
    """Skub alle bolde ud én ad gangen."""
    debug_log(f"Afleverer {ball_count} bolde...")
    for _ in range(ball_count):
        push_balls(motor_push)
        wait(300)

def main():
    ev3.speaker.beep()
    debug_log("GolfBot-EV3 starter...")

    collected = 0
    while collected < BALL_COUNT_MAX:
        drive_forward(200)  # Kør frem til næste bold (justér distance)
        collect_ball()
        collected += 1
        debug_log(f"Bold opsamlet ({collected}/{BALL_COUNT_MAX})")

    go_to_goal()
    deliver_balls(BALL_COUNT_MAX)

    stop_all_motors(motor_left, motor_right, motor_gate, motor_push)
    debug_log("GolfBot-EV3 afslutter programmet.")
    ev3.speaker.beep()

if __name__ == "__main__":
    main()