#!/usr/bin/env pybricks-micropython
import socket
from ev3dev2.motor import LargeMotor, MediumMotor, Motor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor
from ev3dev2.button import Button
from ev3dev2.sound import Sound
from ev3dev2.display import Display
from ev3dev2.wheel import EV3Tire
from ev3dev2.motor import MoveTank
# ----------------------------------------------------------------------
# hardware
# ----------------------------------------------------------------------
sound = Sound()

golfbot = MoveTank(OUTPUT_A, OUTPUT_C)

Motor_LEFT  = LargeMotor(OUTPUT_A)
print("Motor_LEFT initialized")
Motor_RIGHT = LargeMotor(OUTPUT_C)
print("Motor_RIGHT initialized")
Motor_GATE  = Motor(OUTPUT_D)
print("Motor_GATE initialized")
Motor_PUSH  = Motor(OUTPUT_B)
print("Motor_PUSH initialized")



def DriveStrightDist(dist):
    golfbot.straight(-dist)
    return
#+ is right, - is left
def TurnRight(angle_deg):
    golfbot.turn_right(angle = angle_deg)

def TurnLeft(angle_deg):
    golfbot.turn_left(angle = -angle_deg)

def OpenGate():
    Motor_GATE.on(speed=50)
    Motor_GATE.wait_until_not_moving(timeout=300)
    return

def CloseGate():
    Motor_GATE.on(speed=-50)
    Motor_GATE.wait_until_not_moving(timeout=300)
    return


def PushOut():
    Motor_PUSH.on(speed=50)
    Motor_PUSH.wait_until_not_moving(timeout=300)
    return

def PushReturn():
    Motor_PUSH.on(speed=-50)
    Motor_PUSH.wait_until_not_moving(timeout=300)
    return


# ----------------------------------------------------------------------
# TCP server
# ----------------------------------------------------------------------
HOST = "192.168.199.36"          # listen on all interfaces
PORT = 5532       # free port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ← NEW
server_socket.bind((HOST, PORT))
server_socket.listen(1)


while True:
    try:
        # Wait for a client
        conn, addr = server_socket.accept()

        # Receive full script
        received_data = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            received_data += data

        script = received_data.decode("utf-8")

        # Namespace for recognized names
        exec_namespace = {
            #"ev3": ev3,
            #"wait": wait_until_not_moving,
            "Motor_LEFT":  Motor_LEFT,          
            "Motor_RIGHT": Motor_RIGHT,
            "Motor_GATE":  Motor_GATE,
            "Motor_PUSH":  Motor_PUSH,
            "DriveStrightDist": DriveStrightDist,
            "TurnLeft": TurnLeft,
            "TurnRight": TurnRight,
            "CloseGate": CloseGate,
            "OpenGate": OpenGate,
            "PushOut": PushOut,
            "PushReturn": PushReturn,
            "golfbot":     golfbot              
        }

        try:
            exec(script, exec_namespace)       # run the incoming code
            response = "Script executed successfully."
        except Exception as e:
            response = "Execution error: " + str(e)

        conn.send(response.encode("utf-8"))
        conn.close()


    except Exception as err:
        print("Error:", err)
    sound.wait(2000)
