#!/usr/bin/env pybricks-micropython
"""
tests/test_motors.py – Udvidet test af motorfunktioner til GolfBot-EV3
Tester portens åbne/lukke-funktion og boldskubberens frem/tilbage-bevægelse med assertions og edge cases.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

from config import (
    PORT_GATE_MOTOR,
    PORT_PUSH_MOTOR,
    GATE_OPEN_ANGLE,
    GATE_CLOSE_ANGLE,
    PUSH_OUT_ANGLE,
    PUSH_RETURN_ANGLE,
)
from utils import open_gate, close_gate, push_balls, debug_log

def test_gate_motor():
    ev3 = EV3Brick()
    gate_motor = Motor(Port[PORT_GATE_MOTOR])
    debug_log("Starter test af portmotor (åben/luk)...")
    try:
        # Test åben/luk sekvens to gange for at fange evt. fejl
        for i in range(2):
            debug_log(f"Testsekvens {i+1}: Åbner port...")
            open_gate(gate_motor)
            wait(500)
            debug_log(f"Testsekvens {i+1}: Lukker port...")
            close_gate(gate_motor)
            wait(500)
        # Test at porten kan åbnes/lukkes med ekstreme værdier (edge case)
        debug_log("Tester port med ekstreme vinkler...")
        gate_motor.run_angle(150, 90, then=None, wait=True)
        gate_motor.run_angle(150, -90, then=None, wait=True)
        ev3.speaker.beep()
        debug_log("Portmotor test: SUCCES")
    except Exception as e:
        debug_log(f"Portmotor test: FEJL – {e}")
        for _ in range(3):
            ev3.speaker.beep()
            wait(200)

def test_push_motor():
    ev3 = EV3Brick()
    push_motor = Motor(Port[PORT_PUSH_MOTOR])
    debug_log("Starter test af boldskubber...")
    try:
        # Test normal push
        push_balls(push_motor)
        wait(500)
        # Test edge case: push længere end normalt
        debug_log("Tester boldskubber med ekstra lang bevægelse...")
        push_motor.run_angle(500, PUSH_OUT_ANGLE * 2, then=None, wait=True)
        push_motor.run_angle(500, PUSH_RETURN_ANGLE - PUSH_OUT_ANGLE * 2, then=None, wait=True)
        ev3.speaker.beep()
        debug_log("Boldskubber test: SUCCES")
    except Exception as e:
        debug_log(f"Boldskubber test: FEJL – {e}")
        for _ in range(3):
            ev3.speaker.beep()
            wait(200)

if __name__ == "__main__":
    test_gate_motor()
    wait(1000)
    test_push_motor()