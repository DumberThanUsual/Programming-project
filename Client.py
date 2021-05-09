import socket
import time

HOST = '192.168.1.71'  # The server's hostname or IP address
PORT = 12346        # The port used by the server
FORMAT = 'UTF-8'
HEADER = 64

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    s.send(send_length)
    s.send(message)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    send('AUTHENTICATE username:boi password:yea')
    print('hello world')
    time.sleep(1)
    send('fk off')
    print('fk off')
    time.sleep(5)
