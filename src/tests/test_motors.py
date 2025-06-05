#!/usr/bin/env pybricks-micropython
"""
tests/test_motors.py – Test af motorfunktioner til GolfBot-EV3
Tester portens åbne/lukke-funktion og boldskubberens frem/tilbage-bevægelse.
"""

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

from config import (
    PORT_GATE_MOTOR,
    PORT_PUSH_MOTOR,
)
from utils import open_gate, close_gate, push_balls, debug_log

def test_gate_motor():
    ev3 = EV3Brick()
    gate_motor = Motor(Port[PORT_GATE_MOTOR])
    debug_log("Starter test af portmotor (åben/luk)...")
    try:
        open_gate(gate_motor)
        wait(500)
        close_gate(gate_motor)
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
        push_balls(push_motor)
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