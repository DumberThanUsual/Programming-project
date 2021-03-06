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
import time
import threading
import re
import json

HOST = '192.168.1.71'  # The server's hostname or IP address
PORT = 12346        # The port used by the server
FORMAT = 'UTF-8'
HEADER = 64

match = {
    "opponent":None,
    "round":0
}

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
                elif parsedMessage[0] == "MATCHMAKING":
                    matchmakingHandler((parsedMessage[1], parsedMessage[2]))
                elif parsedMessage[0] == "GAME":
                    gameHandler((parsedMessage[1], parsedMessage[2]))
            else:
                connected = False
    disconnect()
    print("Disconnected from server...")
    quit()

def gameHandler(message):
    global match
    if message[0] == "UPDATE":

        value = message[1]["value"]
        key = message[1]["key"]
        try:
            valueType = message[1]["type"]
        except:
            match[key] = value
        else:
            if valueType == "int":
                match[key] = int(value)
            elif valueType == "array":
                match[key] = re.split(",", value)
            else:
                match[key] = value

        try:
            notify = message[1]["notify"]
        except:
            notify = False

        if notify == "true":
            if key == "round":
                if match[key] != 6:
                    print(f"---------------Round number {match['round']}---------------")
                    print()
                else:
                    print("---------------EQUAL SCORES - SUDDEN DEATH---------------")

            elif key == "opponentRolls":
                print(f"{match['opponent']} rolled {match[key][0]} and {match[key][1]}")
                print()
            elif key == "selfRolls":
                print(f"You rolled {match[key][0]} and {match[key][1]}")
                print()

            elif key == "opponentThirdRoll":
                print(f"{match['opponent']} rolled a double and gets a third roll! They rolled a {match[key]}")
                print()
            elif key == "selfThirdRoll":
                print(f"You rolled a double and get a third roll! You rolled a {match[key]}")
                print()

            elif key == "opponentScore":
                print(f"{match['opponent']}'s score is' {match[key]}")
                print()
            elif key == "selfScore":
                print(f"Your score is {match[key]}")
                print()

            elif key == "opponentRoll":
                print(f"{match['opponent']} rolled {match[key]}")
                print()
            elif key == "selfRoll":
                print(f"You rolled {match[key]}")
                print()
    elif message[0] == "END":
        print("---------------END OF MATCH---------------")
        selfScore = message[1]["selfScore"]
        print(f"You scored: {selfScore}")
        opponentScore = message[1]["opponentScore"]
        print(f"{match['opponent']} scored: {opponentScore}")
        if selfScore > opponentScore:
            print("You win!")
        else:
            print("You lose!")
        send("RANKING RANK a:None")

    if message[0] == "RANKING":

        value = message[1]["value"]
        try:
            valueType = message[1]["type"]
        except:
            pass
        else:
            if valueType == "int":
                value = int(value)
            elif valueType == "array":
                value = re.split(",", value)

        try:
            notify = message[1]["notify"]
        except:
            notify = False

        if notify == "true":
            ranks = json.loads(bytearray.fromhex(message[1]["value"]).decode())
            print()
            print("Here are the total ranks:")
            print()
            for player in ranks:
                print(f"{player}: {ranks[str(player)]}")
                print()

def matchmakingHandler(message):
    global matchmakingState
    global match
    if message[0] == "MATCHED":
        matchmakingState = True
        match["opponent"] = message[1]["opponent"]
    elif message[0] == "STATUS":
        if message[1]["status"] == "matching":
            matchmakingState = "matching"


def authenticationHandler(message):
    global authState
    if message[0] == "SUCCESS":
        authState = "SUCCESS"
    elif message[0] == "FAIL":
        authState = "FAIL"

def disconnect():
    conn.close()

#----------MAIN GAME LOOP------------

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

authState = None

while authState == None:
    time.sleep(0.1)

if authState == "SUCCESS":
    print("Successfully logged in")
elif authState == "FAIL":
    print("Unsuccessfull login attempt")
    quit()

matchmakingState = None

send(f'MATCHMAKING JOIN')
print("Joining queue")
print("awaiting server response...")

while matchmakingState != True:
    time.sleep(0.1)
    if matchmakingState == False:
        print("Unable to join queue - matchmaking issue")
        quit()
    if matchmakingState == "matching":
        print("Matching...")
        matchmakingState = None

print("Matched against " + match["opponent"])

while conn:
    time.sleep(1)
