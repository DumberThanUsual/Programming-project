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
import random

HEADER = 64

clientCnt = 0
matchCnt = 0

clients = {}

matching = []

matches = []

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

class Match:
    # ---------ADD MATCHES TO MATCH LIST TO KEEP TRACK -------------------
    def __init__ (self, player1ID, player2ID):
        global matchCnt
        self.ID = matchCnt
        matchCnt += 1
        self.player1ID = player1ID
        self.player1Name = clients[player1ID].name
        self.player1Score = 0
        self.player2ID = player2ID
        self.player2Name = clients[player2ID].name
        self.player2Score = 0
        self.sendToPlayer(f"MATCHED opponent:{self.player2Name}", True, False)
        self.sendToPlayer(f"MATCHED opponent:{self.player1Name}", False, True)
        print(f"[MATCH {player1ID} Vs {player2ID}] - Match starting")
        for i in range(1, 5):
            print(f"[MATCH {self.player1ID} Vs {self.player2ID}] - Round {i}")
            self.sendToPlayer(f"UPDATE key:round value:{i}", True, True)
            self.player1LastState = False
            self.player1State = False
            self.player2LastState = False
            self.player2State = False
            self.sendToPlayer(f"PROMPT type:roll", True, True)
            while not self.player1State and not self.player2State:
                if self.player1LastState != self.player1State:
                    self.player1Rolls = [random.randint(1,6), random.randint(1,6)]
                    self.sendToPlayer(f"UPDATE player:1 key:rolls value:{self.player1Rolls}", True, True)
                    if self.player1rolls[0] == self.player1Rolls [1]:
                        thirdRoll = random.randint(1,6)
                        self.player1Score += thirdRoll
                        self.sendToPlayer(f"UPDATE player:1 key:thirdRoll value:{thirdRoll}", True, True)
                    self.player1Score += self.player1Rolls[0] + self.player1Rolls[1]
                    if self.player1Score % 2 == 0:
                        self.player1Score += 10
                    else:
                        self.player1Score -= 5
                    self.sendToPlayer(f"UPDATE player:2 key:score value:{self.player1Score}", True, True)
                if self.player2LastState != self.player2State:
                    self.player2Rolls = [random.randint(1,6), random.randint(1,6)]
                    self.sendToPlayer(f"UPDATE player:2 key:rolls value:{self.player1Rolls}", True, True)
                    if self.player2rolls[0] == self.player2Rolls [1]:
                        thirdRoll = random.randint(1,6)
                        self.player2Score += thirdRoll
                        self.sendToPlayer(f"UPDATE player:2 key:thirdRoll value:{thirdRoll}", True, True)
                    self.player2Score += self.player2Rolls[0] + self.player2Rolls[1]
                    if self.player2Score % 2 == 0:
                        self.player2Score += 10
                    else:
                        self.player2Score -= 5
                    self.sendToPlayer(f"UPDATE player:2 key:score value:{self.player1Score}", True, True)
                self.player1LastState = self.player1State
                self.player2LastState = self.player2State
            if self.player1Score < 0:
                self.player1Score = 0
            if self.player2Score < 0:
                self.player2Score = 0


    def sendToPlayer(self, message, player1 = False, player2 = False):
        if player1:
            clients[self.player1ID].sendToClient(message)
        if player2:
            clients[self.player2ID].sendToClient(message)

class Client:
    def __init__ (self, conn, addr):
        global clientCnt
        self.ID = clientCnt
        clientCnt += 1
        self.conn = conn
        self.addr = addr
        self.auth = 0
        self.name = "LMAO"

        thread = threading.Thread(target=self.clientConnectionListener)
        thread.start()

    def sendToClient(self, message):
        message = message.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.conn.sendall(send_length)
        self.conn.sendall(message)

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
        for i in range(1, len(components)):
            tempArgs = re.split(":", components[i])
            try:
                args[tempArgs[0]] = tempArgs[1]
            except:
                #error here
                continue


        command = components[0]
        print(command)
        print(args)

                #-----WIP AUTHENTICATION SYSTEM -----#

        if command == "AUTHENTICATE":
            if self.authenticate(args["username"], args["password"]):
                print("auth success")
                self.sendToClient("REEEEEEEEE")
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
            Match(matching[0], matching[1])
            matching.pop(0)
            matching.pop(1)


thread = threading.Thread(target=matchmaking)
thread.start()

while True:
    conn, addr  = s.accept()
    print("[LISTENER]Connection from: " + str(addr))
    tempClient = Client(conn, addr)
    clients[tempClient.ID] = tempClient
