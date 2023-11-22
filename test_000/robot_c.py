import socket as sck

address = ('192.168.1.128', 8000)
isRunning = True

s_client = sck.socket(sck.AF_INET, sck.SOCK_STREAM)

def main():
    global isRunning
    
    s_client.connect(address)

    while isRunning:

        mex = input(">>")

        s_client.sendall(mex.encode())
        text = s_client.recv(4096)
        print(text.decode())

        if text.decode() == "EXIT":
            isRunning = False

    s_client.close()

if __name__=="__main__":
    main()