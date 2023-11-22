"""
Client che invia comandi al robot per muoversi
"""

import socket as sck
import config
from threading import Thread

SERVER_ADDRESS = ("192.168.1.135", 8000)
BUFSIZE = config.BUFSIZE

class Receiver(Thread):
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
        message = input("Inserire un comando (B, F, L, R);tempo(positivo): ")

        client.sendall(message.encode())

    receiver.isRunning = False 

if __name__ == "__main__":
    main()