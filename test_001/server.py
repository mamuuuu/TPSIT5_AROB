"""
Server che riceva i comandi inviati
"""

import socket as sck
import AlphaBot
import config
import time

SERVER_ADDRESS = config.SERVER_ADDRESS
BUFSIZE = config.BUFSIZE

def main():
    server = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)
    server.listen()

    alphabot = AlphaBot.AlphaBot()

    commandDict = {"B": alphabot.backward, "F": alphabot.forward, "L" : alphabot.left, "R" : alphabot.right, "S" : alphabot.stop}

    connection, client_address = server.accept()

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

        connection.sendall(b"messaggio scritto e ricevuto correttamente, movimento svolto")
    
    server.close()

if __name__ == "__main__":
    main()