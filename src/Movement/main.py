#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
ev3 = EV3Brick()

#set motors for wheel:
Motor_LEFT = Motor(Port.A)
Motor_RIGHT = Motor(Port.D)
Motor_GATE = Motor(Port.C)
Motor_PUSH = Motor(Port.B)

#Initialize the "robot"
golfbot = DriveBase(Motor_LEFT, Motor_RIGHT, wheel_diameter=55.5, axle_track=104)

def OpenGatePushOut():

    Motor_GATE.run(150)
    Motor_PUSH.run(-150)
    wait(500)
    return
def CloseGatePushIn():

    Motor_PUSH.run(150)
    wait(300)
    Motor_GATE.run(-150)
    wait(300)
    return

def OpenGate():
    Motor_GATE.run(150)
    wait(300)
    return
def CloseGate():
    Motor_GATE.run(-150)
    wait(300)
    return
def DriveStraight(speed):#delete?
    #oly -100 <= speed <=100
    Motor_LEFT.run(1*(-speed))
    Motor_RIGHT.run(1*(-speed))
    wait(2000)
    return
def DriveStraightTime(time, speed):
    #oly -100 <= speed <=100
    Motor_LEFT.run_time(-speed, time, then=Stop.COAST, wait=False)
    Motor_RIGHT.run_time(-speed, time, then=Stop.COAST, wait=False)
    return
def DriveStrightDist(dist):
    golfbot.straight(-dist)
    return

def TurnLeft(deg):
    Motor_LEFT.run(deg)
    Motor_RIGHT.run(-deg)
    wait(500)
    return

def TurnRight(deg):
    Motor_LEFT.run(-deg)
    Motor_RIGHT.run(deg)
    wait(500)
    return

def TurnOffAllMotors():
    Motor_LEFT.stop()
    Motor_RIGHT.stop()
    Motor_GATE.stop()
    Motor_PUSH.stop()
    return


ev3.speaker.beep()
#TurnLeft(1000)
#golfbot.dc(50)
#Motor_LEFT.dc(-100)
#Motor_RIGHT.dc(-100)

DriveStrightDist(1000)
#DriveStraightTime(2000, 1000)
#DriveStraight(100)
#OpenGatePushOut()
#CloseGatePushIn()
#OpenGate()
#CloseGate()
wait(2000)

#Motor_LEFT.run_target (1500, 90)
#Motor_RIGHT.run_target (500, 90)
#ev3.speaker.say("project SNAFU engaged")
#ev3.speaker.say("Take over the world")
#ev3.speaker.play_notes(['C4/4', 'C4/4', 'G4/4', 'G4/4','C4/4'])

#golfbot.straight(1000)
"""if stop=True, shutdown"""

