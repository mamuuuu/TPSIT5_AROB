"""
Client che invia comandi al robot per muoversi
"""

import socket as sck
import config

SERVER_ADDRESS = ("192.168.1.128", 8000)
BUFSIZE = config.BUFSIZE

def main():
    client = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    client.connect(SERVER_ADDRESS)

    while True:

        message = input("Inserire un comando (B, F, L, R);tempo(positivo): ")

        client.sendall(message.encode())

        data = client.recv(BUFSIZE)

        print(data.decode())

if __name__ == "__main__":
    main()