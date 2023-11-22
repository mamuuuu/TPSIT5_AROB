"""
Server che riceve i comandi inviati e di conseguenza li impartisce al robot
"""
#Librerie necessarie al funzionamento del programma
import RPi.GPIO as GPIO
import socket as sck
import AlphaBot 
import config
import time
from threading import Thread
import sqlite3 as sql

#Costanti
SERVER_ADDRESS = config.SERVER_ADDRESS
BUFSIZE = config.BUFSIZE

class ReceiverSensor(Thread):
    """
    Classe che si occupa di inviare lo stato 
    dei sensori al client
    """
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
    #Creazione dell'end point server
    server = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)
    server.listen()

    alphabot = AlphaBot.AlphaBot()

    #Dizionario dei movimenti possibili oltre a quelli designati ed inseriti nel db
    commandDict = {"B": alphabot.backward, "F": alphabot.forward, "L" : alphabot.left, "R" : alphabot.right, "S" : alphabot.stop}

    #Programma single-thread
    connection, client_address = server.accept()

    receiverSensor = ReceiverSensor(alphabot, connection)
    receiverSensor.start()

    while True:
        messagge = connection.recv(BUFSIZE)
        messagge_decode = messagge.decode()

        #Se non si inserisce ';' significa che non è stato inserito un movimento classico di commandDict, ma uno da ricercare nel db
        if ';' not in messagge_decode:
            #Connessione al db
            connection_db = sql.connect("movements.db")
            cursor_db = connection_db.cursor()
            
            res_db = cursor_db.execute(f"SELECT Mov_sequence FROM Movements WHERE Shortcut = \'{messagge_decode}\'")
            command_list = res_db.fetchall()

            #Controllo della presenza del comando inserito nel db
            if len(command_list) > 0:
                list_command_message = command_list[0][0].split("-")
                
                #Esecuzione della seguenza di comandi
                for command in list_command_message:
                    try:
                        duration = float(command.split(';')[1])
                    except:
                        pass

                    commandDict[command.split(';')[0]]()
                    time.sleep(duration)
                    alphabot.stop()
                connection_db.close()
                continue
            else:
                continue
        #Controllo sulla corretta scrittura del messaggio proveniente dal client
        elif messagge_decode.count(";") > 1:
            connection.sendall(b"Il messaggio contiene troppi ;")
            continue

        command = messagge_decode.split(';')[0]

        if command == "H":
            #invio del menu dei comandi
            connection.sendall(b"I comandi sono F: forward, B: backward, L: left, R: right")
            continue

        #Metodo per uscire
        if command == "E":
            break
        try:
            duration = float(messagge_decode.split(';')[1])
        except:
            pass

        #Controllo sulla presenza del comando nel dizionario dei comandi
        if not(command in commandDict.keys()) and command != "E" and command != "H":
            connection.sendall(b"il comando inserito non e' presente nella lista")
            continue
        #Controllo sulla durata del comando inserito
        if duration < 0:
            connection.sendall(b"il valore inserito e' negativo")
            continue
        
        commandDict[command]()
        time.sleep(duration)
        alphabot.stop()
    
    #Chiusura del thread
    receiverSensor.isRunning = False
    receiverSensor.join()
    
    #Chiusura del server
    server.close()

if __name__ == "__main__":
    main()