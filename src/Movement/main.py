#!/usr/bin/env pybricks-micropython
"""
drive_utils.py  – Straight, reverse and in-place turns with ev3dev2.
Works with any wheel class once you give its diameter.
"""

import socket, _thread, time
from queue import Queue

# ── Imports ───────────────────────────────────────────────────────────
from ev3dev2.tool import Tool
from ev3dev2.motor import Motor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, MoveDifferential, SpeedRPM
from ev3dev2.wheel import Wheel

# ----------------------------------------------------------------------
# hardware
# ----------------------------------------------------------------------
Motor_GATE  = Motor(OUTPUT_D)
print("Motor_GATE initialized")
Motor_PUSH  = Motor(OUTPUT_A)
print("Motor_PUSH initialized")

# ── Constants you set once ────────────────────────────────────────────
STUD_MM            = 8.0
WHEEL_DISTANCE_MM  = 50.0

# ── Wheel geometry (68.8 × 36 ZR tyre) ────────────────────────────────
class Tire68836ZR(Wheel):
    def __init__(self):
        super().__init__(68.8, 36.0)

# ── Drive base object --------------------------------------------------
mdiff = MoveDifferential(
    OUTPUT_B, OUTPUT_C,
    Tire68836ZR,
    WHEEL_DISTANCE_MM
)
print("MoveDifferential initialized with wheels on ports B and C.")

def wait_until_stopped(timeout_ms: int = 300):
    start_time = time.time()
    stopped = False
    while ((time.time() - start_time) * 1000) < timeout_ms:
        left_running = 'running' in mdiff.left_motor.state
        right_running = 'running' in mdiff.right_motor.state
        if not left_running and not right_running:
            stopped = True
            break
        time.sleep(0.05)
    if not stopped:
        print("Warning: Motors did not stop within timeout.")

def _apply_ramps(ramp_ms: int) -> None:
    for m in (mdiff.left_motor, mdiff.right_motor):
        m.ramp_up_sp = ramp_ms
        m.ramp_down_sp = ramp_ms

def drive_straight_mm(distance_mm: float,
                      speed_rpm: float = 60,
                      ramp_ms: int = 300,
                      brake: bool = True,
                      block: bool = True) -> None:
    _apply_ramps(ramp_ms)
    mdiff.on_for_distance(SpeedRPM(speed_rpm), distance_mm, brake=brake, block=block)
    wait_until_stopped(timeout_ms=300)

def reverse_drive_mm(distance_mm: float,
                     speed_rpm: float = 60,
                     ramp_ms: int = 300,
                     brake: bool = True,
                     block: bool = True) -> None:
    drive_straight_mm(-abs(distance_mm), speed_rpm, ramp_ms, brake, block)
    wait_until_stopped(timeout_ms=300)

def turn_deg(angle_deg: float,
             speed_rpm: float = 40,
             ramp_ms: int = 300,
             brake: bool = True,
             block: bool = True) -> None:
    _apply_ramps(ramp_ms)
    if angle_deg >= 0:
        mdiff.turn_right(SpeedRPM(speed_rpm), angle_deg, brake=brake, block=block)
    else:
        mdiff.turn_left(SpeedRPM(speed_rpm), -angle_deg, brake=brake, block=block)
    wait_until_stopped(timeout_ms=300)

def stop_drive(brake: bool = True) -> None:
    mdiff.off(brake=brake)

def turn_right_deg(angle_deg):
    Motor_GATE.off()
    Motor_PUSH.off()
    turn_deg(angle_deg)
    Motor_GATE.wait_until_not_moving(timeout=300)
    Motor_PUSH.wait_until_not_moving(timeout=300)
    return

def turn_left_deg(angle_deg):
    Motor_GATE.off()
    Motor_PUSH.off()
    turn_deg(-angle_deg)
    Motor_GATE.wait_until_not_moving(timeout=300)
    Motor_PUSH.wait_until_not_moving(timeout=300)
    return

def open_gate():
    mdiff.off(brake=True)
    Motor_PUSH.off()
    Motor_GATE.on(speed=5)
    Motor_GATE.wait_until_not_moving(timeout=300)
    mdiff.wait_until_not_moving(timeout=300)
    Motor_GATE.wait_until_not_moving(timeout=300)
    return

def close_gate():
    mdiff.off(brake=True)
    Motor_PUSH.off()
    Motor_GATE.on(speed=-5)
    Motor_GATE.wait_until_not_moving(timeout=300)
    mdiff.wait_until_not_moving(timeout=300)
    Motor_GATE.wait_until_not_moving(timeout=300)
    return

def push_out():
    mdiff.off(brake=True)
    Motor_GATE.off()
    Motor_PUSH.on(speed=-5)
    Motor_PUSH.wait_until_not_moving(timeout=300)
    mdiff.wait_until_not_moving(timeout=300)
    Motor_PUSH.wait_until_not_moving(timeout=300)
    return

def push_return():
    mdiff.off(brake=True)
    Motor_GATE.off()
    Motor_PUSH.on(speed=5)
    Motor_PUSH.wait_until_not_moving(timeout=300)
    mdiff.wait_until_not_moving(timeout=300)
    Motor_PUSH.wait_until_not_moving(timeout=300)
    return

# ----------------------------------------------------------------------
# TCP server
# ----------------------------------------------------------------------
HOST = "192.168.147.36"
PORT = 5532

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

command_queue = Queue()

def listener():
    while True:
        conn, addr = server_socket.accept()
        command_data = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command_data += data
        command = command_data.decode("utf-8")
        print("Received command:", command)
        command_queue.put((command, conn))

def command_processor():
    while True:
        command, conn = command_queue.get()
        exec_namespace = {
            "turn_left_deg": turn_left_deg,
            "turn_right_deg": turn_right_deg,
            "drive_straight_mm": drive_straight_mm,
            "reverse_drive_mm": reverse_drive_mm,
            "open_gate": open_gate,
            "close_gate": close_gate,
            "push_out": push_out,
            "push_return": push_return,
            "stop_drive": stop_drive,
            "mdiff": mdiff,
            "Motor_GATE": Motor_GATE,
            "Motor_PUSH": Motor_PUSH,
        }
        try:
            exec(command, exec_namespace)
            response = "Command executed successfully.\n {command}".format(command=command)
        except Exception as e:
            response = "Execution error: {}\n".format(e)
        try:
            conn.sendall(response.encode("utf-8"))
        except Exception as e:
            print("Error sending response:", e)
        conn.close()
        print("Finished processing command.")

try:
    _thread.start_new_thread(listener, ())
    _thread.start_new_thread(command_processor, ())
except Exception as err:
    print("Error starting threads:", err)

while True:
    time.sleep(1)