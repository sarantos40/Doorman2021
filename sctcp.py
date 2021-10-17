#!/usr/bin/python3
# https://realpython.com/python-sockets/
import socket
import sys
from PIL import Image
import io

PORT = 65432
echo = False

def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', PORT))
        while True: 
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                alldata = b''
                while True:
                    data = conn.recv(1024000)
                    alldata += data
                    if echo: print('Got', len(data))
                    if not data: break
                im = Image.open(io.BytesIO(alldata))
                im.show()


def client(host, msg):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #if s.connect_ex((host, PORT)) == 0:
            #    print("Port is open")
            #else:
            #    print("Port is not open")
            s.connect((host, PORT))
            s.sendall(msg)
            if echo: print('Sent', len(msg))
    except (ConnectionRefusedError) as e:
        print(f'Unable to communicate to {host}: {e}')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        server()
    elif len(sys.argv) == 2:
        client('127.0.0.1', open(sys.argv[1], 'rb').read())
    else:
        client(sys.argv[1], open(sys.argv[2], 'rb').read())
