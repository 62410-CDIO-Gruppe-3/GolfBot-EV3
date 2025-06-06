#!/usr/bin/env pybricks-micropython
import socket
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# ----------------------------------------------------------------------
# hardware
# ----------------------------------------------------------------------
ev3 = EV3Brick()

Motor_LEFT  = Motor(Port.A)
Motor_RIGHT = Motor(Port.D)
Motor_GATE  = Motor(Port.C)
Motor_PUSH  = Motor(Port.B)

golfbot = DriveBase(Motor_LEFT, Motor_RIGHT,
                    wheel_diameter=55.5, axle_track=100)
def DriveStrightDist(dist):
    golfbot.straight(-dist)
    return
#+ is right, - is left
def TurnRight(angle_deg):
    golfbot.turn(angle_deg)
def TurnLeft(angle_deg):
    golfbot.turn(-angle_deg)
def OpenGate():
    Motor_GATE.run(150)
    wait(300)
    return
def CloseGate():
    Motor_GATE.run(-150)
    wait(300)
    return
def PushOut():
    Motor_PUSH.run(150)
    wait(300)
    return
def PushReturn():
    Motor_PUSH.run(-150)
    wait(300)
    return


# ----------------------------------------------------------------------
# TCP server
# ----------------------------------------------------------------------
HOST = ''          # listen on all interfaces
PORT = 5532       # free port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ← NEW
server_socket.bind((HOST, PORT))
server_socket.listen(1)

ev3.screen.clear()
ev3.screen.draw_text(0, 10, "Send to:")
ev3.screen.draw_text(0, 30, "Port {}".format(PORT))

while True:
    try:
        # Wait for a client
        conn, addr = server_socket.accept()
        ev3.screen.clear()
        ev3.screen.draw_text(0, 10, "Connected from:")
        ev3.screen.draw_text(0, 30, "{}".format(addr))

        # Receive full script
        received_data = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            received_data += data

        script = received_data.decode("utf-8")

        ev3.screen.clear()
        ev3.screen.draw_text(0, 10, "Executing…")

        # Namespace for recognized names
        exec_namespace = {
            "ev3": ev3,
            "wait": wait,
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

        ev3.screen.clear()
        ev3.screen.draw_text(0, 10, "Ready for new conn.")

    except Exception as err:
        ev3.speaker.beep()
        ev3.screen.clear()
        ev3.screen.draw_text(0, 10, "Server error:")
        ev3.screen.draw_text(0, 30, str(err))
    wait(2000)
