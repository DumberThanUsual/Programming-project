import socket
import time
import threading
import re

HOST = '192.168.1.71'  # The server's hostname or IP address
PORT = 12346        # The port used by the server
FORMAT = 'UTF-8'
HEADER = 64

authState = None

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)

def parseMessage(message):
    args = {}
    components = re.split("\s+", message)
    for i in range(2, len(components)):
        tempArgs = re.split(":", components[i])
        args[tempArgs[0]] = tempArgs[1]
    return (components[0], components[1],  args)

def connectionListener(conn):
    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except Exception as error:
            connected = False
        else:
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                parsedMessage = parseMessage(msg)
                if parsedMessage[0] == "AUTHENTICATE":
                    authenticationHandler((parsedMessage[1], parsedMessage[2]))
            else:
                connected = False
    disconnect()
    print("Disconnected from server...")
    quit()

def authenticationHandler(message):
    global authState
    if message[0] == "SUCCESS":
        authState = "SUCCESS"
    elif message[0] == "FAIL":
        authState = "FAIL"

def disconnect():
    conn.close()

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    conn.connect((HOST, PORT))
except Exception as error:
    print("Unable to connect to server:")
    print("%s" % error)
    quit()
thread = threading.Thread(target=connectionListener, args=(conn,))
thread.start()
username = input("username:")
password = input("password:")
send(f'AUTHENTICATE AUTHENTICATE username:{username} password:{password}')

while authState == None:
    time.sleep(0.1)

if authState == "SUCCESS":
    print("Successfully logged in")
elif authState == "FAIL":
    print("Unsuccessfull login attempt")
    quit()
time.sleep(500)
