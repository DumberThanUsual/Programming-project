'''
    Copyright (C) 2021 Yuki Hoshino - Computing Programming Project

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import socket
import threading
import time
import sys
import hashlib
import re

HEADER = 64

HashCnt = 0

clients = {}

matching = []

HOST = socket.gethostbyname(socket.gethostname())
PORT = 12346
FORMAT = 'UTF-8'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
  s.bind((HOST, PORT))
except:
  print("[LISTENER] - Bind failed. Error : " + str(sys.exc_info()))
  sys.exit()

s.listen(5)
print("[LISTENER] - Server listening on: " + str(HOST) + ", port: " + str(PORT))

class Client:
    def __init__ (self, conn, addr):
        global HashCnt
        self.ID = HashCnt
        HashCnt += 1
        self.conn = conn
        self.addr = addr
        self.auth = 0

        thread = threading.Thread(target=self.clientConnectionListener)
        thread.start()

    def sendAllToClient(self, message):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        s.send(send_length)
        s.sendall(message)

    def checkAuth(self):
        return True

    def authenticate(self, username, password):
        return True

    def disconnect(self):
        pass

    def parseMessage(self, message):
        args = {}
        try:
            components = re.split("\s+", message)
        except:
            #error here
            pass
        print(components)
        for i in range(1, len(components)):
            tempArgs = re.split(":", components[i])
            try:
                args[tempArgs[0]] = tempArgs[1]
            except:
                #error here
                continue

        print(args)

        #-----WIP AUTHENTICATION SYSTEM -----#
        command = components[0]
        if command == "AUTHENTICATE":
            if self.authenticate(args["username"], args["password"]):
                print("auth success")
                #GENERATE TOKEN ETC
                matching.append(self.ID)
            else:
                pass
                #SEND ERROR TO CLIENT
        #elif command == ""


    def clientConnectionListener(self):
        connected = True
        print("[ClientConnectionListener] - New thread started for " + addr[0] + ":" + str(addr[1]))
        while connected:
            try:
                msg_length = conn.recv(HEADER).decode(FORMAT)
            except Exception as error:
                print("[ClientConnectionListener] - Disconnecting - Connection error from " + addr[0] + ":" + str(addr[1]) + " - %s" % error)
                connected = False
            else:
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    print(f"[{addr}] {msg}")
                    self.parseMessage(msg)
                else:
                    print("[ClientConnectionListener] - Disconnecting - " + addr[0] + ":" + str(addr[1]) + " closed the connection")
                    connected = False
        conn.close()
        self.disconnect()
        print("[ClientConnectionListener] - Disconnected - " + addr[0] + ":" + str(addr[1]))

def matchmaking():
    while True:
        if len(matching) >= 2:
            print("match")

thread = threading.Thread(target=matchmaking)
thread.start()

while True:
    conn, addr  = s.accept()
    print("[LISTENER]Connection from: " + str(addr))
    tempClient = Client(conn, addr)
    clients[tempClient.ID] = tempClient
