"""
utils.py – Genanvendelige hjælpefunktioner til GolfBot-EV3
Indeholder funktioner til motorstyring, portkontrol og boldhåndtering.
Alle parametre og porte importeres fra config.py.
"""

from pybricks.tools import wait
from pybricks.parameters import Stop
from config import (
    GATE_OPEN_ANGLE,
    GATE_CLOSE_ANGLE,
    GATE_MOTOR_SPEED,
    GATE_WAIT_TIME,
    PUSH_OUT_ANGLE,
    PUSH_RETURN_ANGLE,
    PUSH_MOTOR_SPEED,
    PUSH_WAIT_TIME,
    DEBUG,
)

def debug_log(message):
    """
    Udskriver debug-beskeder, hvis DEBUG er True i config.py.
    """
    if DEBUG:
        print(f"[DEBUG] {message}")

def open_gate(motor):
    """
    Åbner porten med defineret vinkel og hastighed, venter derefter.
    """
    try:
        debug_log("Åbner porten...")
        motor.run_angle(GATE_MOTOR_SPEED, GATE_OPEN_ANGLE, then=Stop.BRAKE, wait=True)
        wait(GATE_WAIT_TIME)
        debug_log("Porten er åben.")
    except Exception as e:
        debug_log(f"Fejl ved åbning af port: {e}")

def close_gate(motor):
    """
    Lukker porten med defineret vinkel og hastighed, venter derefter.
    """
    try:
        debug_log("Lukker porten...")
        motor.run_angle(GATE_MOTOR_SPEED, GATE_CLOSE_ANGLE, then=Stop.BRAKE, wait=True)
        wait(GATE_WAIT_TIME)
        debug_log("Porten er lukket.")
    except Exception as e:
        debug_log(f"Fejl ved lukning af port: {e}")

def push_balls(motor):
    """
    Skubber bolde frem med høj hastighed og returnerer til startposition.
    """
    try:
        debug_log("Skubber bolde ud...")
        motor.run_angle(PUSH_MOTOR_SPEED, PUSH_OUT_ANGLE, then=Stop.BRAKE, wait=True)
        wait(PUSH_WAIT_TIME)
        debug_log("Returnerer boldskubber til startposition...")
        motor.run_angle(PUSH_MOTOR_SPEED, PUSH_RETURN_ANGLE - PUSH_OUT_ANGLE, then=Stop.BRAKE, wait=True)
        debug_log("Boldskubber er tilbage ved start.")
    except Exception as e:
        debug_log(f"Fejl ved boldskub: {e}")

def stop_all_motors(*motors):
    """
    Stopper alle angivne motorer med bremse.
    """
    for motor in motors:
        try:
            motor.stop()
            debug_log(f"Motor {motor} stoppet.")
        except Exception as e:
            debug_log(f"Fejl ved stop af motor {motor}: {e}")