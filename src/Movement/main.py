#!/usr/bin/env pybricks-micropython
"""
drive_utils.py  – Straight, reverse and in-place turns with ev3dev2.
Works with any wheel class once you give its diameter.
"""

import socket, _thread, time
from queue import Queue

# ── Imports ───────────────────────────────────────────────────────────
from ev3dev2.motor import OUTPUT_B, OUTPUT_C, MoveDifferential, SpeedRPM
from ev3dev2.wheel import Wheel
#!/usr/bin/env pybricks-micropython
import socket
from ev3dev2.motor import Motor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
# ----------------------------------------------------------------------
# hardware
# ----------------------------------------------------------------------
Motor_GATE  = Motor(OUTPUT_D)
print("Motor_GATE initialized")
Motor_PUSH  = Motor(OUTPUT_A)
print("Motor_PUSH initialized")
# ── Constants you set once ────────────────────────────────────────────
STUD_MM            = 8.0      # LEGO grid pitch – keep at 8 mm
WHEEL_DISTANCE_MM  = 137.53    # centre-to-centre spacing of your wheels

# ── Wheel geometry (68.8 × 36 ZR tyre) ────────────────────────────────
class Tire68836ZR(Wheel):
    """LEGO® tyre 68.8 mm Ø × 36 mm (part 44771)."""
    def __init__(self):
        super().__init__(68.8, 36.0)      # diameter, width [mm]

# ── Drive base object --------------------------------------------------
mdiff = MoveDifferential(
    OUTPUT_B, OUTPUT_C,          # motor ports – change if needed
    Tire68836ZR,                 # wheel dimensions
    WHEEL_DISTANCE_MM            # ← track-width constant above
)
print("MoveDifferential initialized with wheels on ports B and C.")

def wait_until_stopped(timeout_ms: int = 300):
    """
    Wait until both drive motors have stopped (i.e. are no longer running)
    or until the timeout (in milliseconds) has been reached.
    """
    start_time = time.time()
    stopped = False
    while ((time.time() - start_time) * 1000) < timeout_ms:
        # Check the state of each motor. (Adjust based on the API your motors offer.)
        left_running = 'running' in mdiff.left_motor.state
        right_running = 'running' in mdiff.right_motor.state
        if not left_running and not right_running:
            stopped = True
            break
        time.sleep(0.05)
    if not stopped:
        print("Warning: Motors did not stop within timeout.")

# ── Shared helper to set smooth ramps on both motors ──────────────────
def _apply_ramps(ramp_ms: int) -> None:
    for m in (mdiff.left_motor, mdiff.right_motor):
        m.ramp_up_sp   = ramp_ms
        m.ramp_down_sp = ramp_ms

# ── Public helpers ────────────────────────────────────────────────────
def drive_straight_mm(distance_mm: float,
             speed_rpm: float = 60,
             ramp_ms:   int   = 300,
             brake:     bool  = True,
             block:     bool  = True) -> None:
    """Drive straight (forward + / reverse –) for distance_mm millimetres."""
    _apply_ramps(ramp_ms)
    mdiff.on_for_distance(
        SpeedRPM(speed_rpm),
        distance_mm,
        brake=brake,
        block=block
    )


def reverse_drive_mm(distance_mm: float,
                  speed_rpm: float = 60,
                  ramp_ms:   int   = 300,
                  brake:     bool  = True,
                  block:     bool  = True) -> None:
    """Drive backward for *distance_mm* (positive value)."""
    drive_straight_mm(-abs(distance_mm), speed_rpm, ramp_ms, brake, block)


def turn_deg(angle_deg: float,
             speed_rpm: float = 40,
             ramp_ms:   int   = 300,
             brake:     bool  = True,
             block:     bool  = True) -> None:
    """
    Spin in place by *angle_deg* degrees.
    +ve ⇒ clockwise, –ve ⇒ counter-clockwise.
    """
    _apply_ramps(ramp_ms)

    # MoveDifferential already has turn helpers
    # (turn_right / turn_left) we can delegate to:
    if angle_deg >= 0:
        mdiff.turn_right(SpeedRPM(speed_rpm),  angle_deg,
                         brake=brake, block=block)   # :contentReference[oaicite:0]{index=0}
        #mdiff.wait_until_not_moving(timeout=300)
    else:
        mdiff.turn_left(SpeedRPM(speed_rpm),  -angle_deg,
                        brake=brake, block=block)    # :contentReference[oaicite:1]{index=1}
        #mdiff.wait_until_not_moving(timeout=300)

def stop_drive(brake: bool = True) -> None:
    """
    **Immediate stop** for both drive motors.

    Parameters
    ----------
    brake : True  → active braking (default, holds position)  
            False → coast to a rest
    """
    mdiff.off(brake=brake)


def turn_right_deg(angle_deg):
    turn_deg(angle_deg)
    return

def turn_left_deg(angle_deg):
    turn_deg(-angle_deg)
    return

def open_gate():
    Motor_GATE.off()
    time.sleep(1)
    Motor_GATE.on(speed=20)
    time.sleep(1)  # <-- vent så længe du vil køre motoren
    Motor_GATE.off() 
   # Motor_GATE.wait_until_not_moving(timeout=300)  
    return

def close_gate():
    Motor_GATE.off()
    time.sleep(1)
    Motor_GATE.on(speed=-20)
    time.sleep(2)  # <-- vent så længe du vil køre motoren
    Motor_GATE.off()
    #Motor_GATE.wait_until_not_moving(timeout=300)  
    return

def push_out():
    Motor_PUSH.on(speed=-20)
    time.sleep(2)  # <-- vent så længe du vil køre motoren
    Motor_PUSH.off()
   # Motor_PUSH.wait_until_not_moving(timeout=300)
    return

def push_return():
    Motor_PUSH.on(speed=20)
    time.sleep(1)  # <-- vent så længe du vil køre motoren
    Motor_PUSH.off()
   # Motor_PUSH.wait_until_not_moving(timeout=300)
    return

def turn_off_all_motors():
    mdiff.off()
    Motor_GATE.off()
    Motor_PUSH.off()
    return


# ----------------------------------------------------------------------
# TCP server
# ----------------------------------------------------------------------
HOST = "172.20.10.4"          # listen on all interfaces
PORT = 5532       # free port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ← NEW
server_socket.bind((HOST, PORT))
server_socket.listen(1)

#print(f"EV3 Server listening on port", {PORT}, "at", {HOST}, "(press Ctrl+C to stop)")

# Shared command queue for incoming scripts
command_queue = Queue()


def listener():
    """
    Accepts incoming connections and queues their commands.
    """
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
    """
    Retrieves commands from the queue and executes them sequentially.
    """
    while True:
        command, conn = command_queue.get()
        # Create an execution namespace that contains all available commands.
        exec_namespace = {
            "turn_left_deg": turn_left_deg,
            "turn_right_deg": turn_right_deg,
            "drive_straight_mm": drive_straight_mm,
            "open_gate": open_gate,
            "close_gate": close_gate,
            "push_out": push_out,
            "push_return": push_return,
            "stop_drive": stop_drive,
            "turn_off_all_motors": turn_off_all_motors,
            "stop_all_motors": turn_off_all_motors,
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

# Start listener and processor threads:
try:
    _thread.start_new_thread(listener, ())
    _thread.start_new_thread(command_processor, ())
except Exception as err:
    print("Error starting threads:", err)

# Keep the main thread alive.
while True:
    time.sleep(1)