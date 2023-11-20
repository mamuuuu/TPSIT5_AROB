"""
Client che invia comandi al robot per impartirne il movimento
"""
#Librerie necessarie al funzionamento del programma
import socket as sck
import config
from threading import Thread

#Costanti
SERVER_ADDRESS = ("192.168.1.135", 8000)
BUFSIZE = config.BUFSIZE

class Receiver(Thread):
    """
    Classe che si occupa di attendere e ricevere messaggi 
    sullo stato dei sensori del robot
    """
    def __init__(self, client: sck.socket):
        Thread.__init__(self)
        self.client = client
        self.isRunning = True
    
    def run(self):
        while self.isRunning is True:
            data = self.client.recv(BUFSIZE)
            print(data.decode())

def main():
    client = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    client.connect(SERVER_ADDRESS)
    
    receiver = Receiver(client)
    receiver.start()

    while True:
        message = input("Inserire un comando;durata: ")

        client.sendall(message.encode())
    
    #Chiusura thread
    receiver.isRunning = False
    receiver.join()

    #Chiusura client
    client.close()

if __name__ == "__main__":
    main()