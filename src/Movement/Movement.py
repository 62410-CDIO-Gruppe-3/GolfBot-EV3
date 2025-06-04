#!/usr/bin/env pybricks-micropython
import socket
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
#motors:
Motor_LEFT = Motor(Port.A)
Motor_RIGHT = Motor(Port.D)
Motor_GATE = Motor(Port.C)
Motor_PUSH = Motor(Port.B)
golfbot = DriveBase(Motor_LEFT, Motor_RIGHT, wheel_diameter=55.5, axle_track=100)


#server:
HOST = ''   #listen on network
PORT = 5532 #free port

# Create and configure the server socket.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
#ev3 display:
ev3.screen.clear()
ev3.screen.draw_text(0, 10, "Send to:")
ev3.screen.draw_text(0, 30, "Port {}".format(PORT))

while True:
    #Copilot helped:
    try:
        # Wait for a client to connect.
        conn, addr = server_socket.accept()
        ev3.screen.clear()
        ev3.screen.draw_text(0, 10, "Connected from:")
        ev3.screen.draw_text(0, 30, "{}".format(addr))
        
        # Receive script.
        received_data = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            received_data += data
        
        # Decode the received bytes into a UTF-8 string.
        script = received_data.decode("utf-8")
        ev3.screen.clear()
        ev3.screen.draw_text(0, 10, "Executing script:")
                
        # Prepare a namespace for the exec() call.
        # Including the ev3 object (and any other safe functions) so that remote scripts can access it.
        exec_namespace = {"ev3": ev3, "wait": wait, "golfbot": golfbot, "Motor_PUSH": Motor_PUSH, "Motor_LEFT": Motor_LEFT}
        
        try:
            # Execute the received script.
            exec(script, exec_namespace)
            response = "Script executed successfully."
        except Exception as e:
            response = "Execution error: " + str(e)
        
        # Send the response back to the client.
        conn.send(response.encode("utf-8"))
        conn.close()
        
        # After running the script, return to listening.
        ev3.screen.clear()
        ev3.screen.draw_text(0, 10, "Ready for new conn.")
    except Exception as err:
        ev3.speaker.beep()
        ev3.screen.clear()
        ev3.screen.draw_text(0, 10, "Server error:")
        ev3.screen.draw_text(0, 30, str(err))
    wait(2000)



    
    
    
    #ev3.speaker.beep()
    #wait(2000)
