import socket

EV3_IP = '192.168.43.36'    #ev3 ip
PORT = 5532                 #port thats being listened on


script1 = """
ev3.speaker.beep(20)
wait(200)
ev3.speaker.beep(100)
wait(200)
ev3.speaker.beep(200)
wait(200)
"""
script2 = """
ev3.speaker.beep(200)
wait(200)
ev3.speaker.beep(200)
wait(200)
ev3.speaker.beep(200)
wait(200)
"""
StopMotor = False

#DriveStraight500 = """Motor_LEFT.run(1*(500))"""
#StopDrive = """Motor_LEFT.run(0)"""

#distance vars etc
ForwardMM = -500
DegreeTurn = 45


def SendRecieve(script):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((EV3_IP, PORT))
        client_socket.sendall(script.encode("utf-8"))        
        #done sending and ready to close connection
        client_socket.shutdown(socket.SHUT_WR)
        response = client_socket.recv(1024)
        return response.decode("utf-8")


def main_loop():
    message = script1
    while True:
        ReplyFromEV = SendRecieve(message)
        print("EV3: ", ReplyFromEV)

        KeyboardRead = input("Q to exit, enter to repeat")
        if KeyboardRead.strip().lower() == "q":
            #needs to stop the motor etc before breaking if running etc
            #StopMotor = True
            break
        if KeyboardRead.strip().lower() == "a":
            message = f"TurnLeft({DegreeTurn})"
        if KeyboardRead.strip().lower() == "s":
            message = f"TurnRight({DegreeTurn})"
        if KeyboardRead.strip().lower() == "w":
            message = f"DriveStrightDist({ForwardMM})"
        
        if KeyboardRead.strip().lower() == "p":
            message = script1
        if KeyboardRead.strip().lower() == "o":
            message = script2
        if KeyboardRead.strip().lower() == "x":
            #message = StopDrive
            message = script1
            







if __name__ == "__main__":
    main_loop()