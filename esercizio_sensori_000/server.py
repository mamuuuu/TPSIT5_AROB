"""
Server che riceva i comandi inviati
"""
import RPi.GPIO as GPIO
import socket as sck
import AlphaBot
import config
import time
from threading import Thread

SERVER_ADDRESS = config.SERVER_ADDRESS
BUFSIZE = config.BUFSIZE

class ReceiverSensor(Thread):
    def __init__(self, alphabot : AlphaBot.AlphaBot, connection : sck.socket):
        Thread.__init__(self)
        self.DR = 16
        self.DL = 19
        self.alphabot = alphabot
        self.connection = connection
        self.isRunning = True
        self.DL_status, self.DR_status = None, None
        self.sensor_dx_active = False
        self.sensor_sx_active = False
        self.sensor_all_active = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.DR,GPIO.IN,GPIO.PUD_UP)
        GPIO.setup(self.DL,GPIO.IN,GPIO.PUD_UP)
    
    def run(self):
        try:
            while self.isRunning is True:
                self.DR_status = GPIO.input(self.DR)	#Statue of anterior right sensor
                self.DL_status = GPIO.input(self.DL)	#Statue of anterior left sensor
                # if DL_* == 1: not detention
                # if DL_* == 0: detention
                if((self.DL_status == 1) and (self.DR_status == 1)):
                    pass

                elif((self.DL_status == 1) and (self.DR_status == 0)):
                    #self.alphabot.stop()
                    if not self.sensor_dx_active:
                        self.connection.sendall(b">> WARNING: anterior right sensor detetcts an obstacle!")
                        self.sensor_sx_active = False
                        self.sensor_all_active = False
                    #self.alphabot.left()
                    #time.sleep(0.2)
                    #self.alphabot.stop()
                    self.sensor_dx_active = True

                elif((self.DL_status == 0) and (self.DR_status == 1)):
                    #self.alphabot.stop()
                    if not self.sensor_sx_active:
                        self.connection.sendall(b">> WARNING: anterior left sensor detetcts an obstacle!")
                        self.sensor_dx_active = False
                        self.sensor_all_active = False
                    #self.alphabot.right()
                    #time.sleep(0.2)
                    #self.alphabot.stop()
                    self.sensor_sx_active = True
                else:
                    #self.alphabot.stop()
                    if not self.sensor_all_active:
                        self.connection.sendall(b">> WARNING: anterior both sensors detetct an obstacle!")
                        self.sensor_dx_active = False
                        self.sensor_sx_active = False
                    #self.alphabot.backward()
                    #time.sleep(0.5)
                    #self.alphabot.stop()
                    self.sensor_all_active = True
                time.sleep(0.5)

        except KeyboardInterrupt:
            GPIO.cleanup()

def main():

    server = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)
    server.listen()

    alphabot = AlphaBot.AlphaBot()

    commandDict = {"B": alphabot.backward, "F": alphabot.forward, "L" : alphabot.left, "R" : alphabot.right, "S" : alphabot.stop}

    connection, client_address = server.accept()

    receiverSensor = ReceiverSensor(alphabot, connection)
    receiverSensor.start()

    while True:
        messagge = connection.recv(BUFSIZE)
        messagge_decode = messagge.decode()

        if ';' not in messagge_decode:
            connection.sendall(b"Il messaggio non contiene il ;")
            continue
        elif messagge_decode.count(";") > 1:
            connection.sendall(b"Il messaggio contiene troppi ;")
            continue

        command = messagge_decode.split(';')[0]

        if command == "H":
            connection.sendall(b"I comandi sono F: forward, B: backward, L: left, R: right")
            continue

        #Metodo per uscire
        if command == "E":
            break
        try:
            time_value = float(messagge_decode.split(';')[1])
        except:
            pass

        if not(command in commandDict.keys()) and command != "E" and command != "H":
            connection.sendall(b"il comando inserito non e' presente nella lista")
            continue
        
        if time_value < 0:
            connection.sendall(b"il valore inserito e' negativo")
            continue
        
        commandDict[command]()
        time.sleep(time_value)
        alphabot.stop()

        #connection.sendall(b"messaggio scritto e ricevuto correttamente, movimento svolto")
        #data = f"I dati dei sensori sono:\nSensore di sinistra: {receiverSensor.DL_status}\nSensore di destra: {receiverSensor.DR_status}\n".encode()
        #connection.sendall(data)
    
    server.close()
    receiverSensor.isRunning = False

if __name__ == "__main__":
    main()