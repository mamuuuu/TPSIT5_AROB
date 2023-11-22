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
        self.alphabot = alphabot
        self.connection = connection
        self.isRunning = True
    
    def run(self):
        try:
            while self.isRunning is True:
                string : str = self.alphabot.get_sensor() + ""
                self.connection.sendall(string.encode())

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