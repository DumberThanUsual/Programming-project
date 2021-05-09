'''
  Copyright (C) 2018  Yuki Hoshino

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
##import libraries

import socket
import time
import json
from _thread import *
import hashlib
import sys

##set server info vaiables

version = [0, 0, 1]
SRVName = "Game Server"
WaitingRoomName = "WaitingRoom"
PlayerTimeout = 10

##set game details

options = {
    "Rock": {
        "Name": "Rock",
        "Beats": ["Scissors"],
        "DefeatedBy": ["Paper"]
    },
    "Paper": {
        "Name": "Paper",
        "Beats": ["Rock"],
        "DefeatedBy": ["Paper"]
    },
    "Scissors": {
        "Name": "Scissors",
        "Beats": ["Paper"],
        "DefeatedBy": ["Rock"]
    }
}

##set server connection variables

HOST = '0.0.0.0'
PORT = 12346

##establish socket server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

##set class objects

class PlayerRoom:
    def __init__(self, RoomName):
        self.RoomName = RoomName
        self.Players = []
        self.PlayerCount = len(self.Players)
    def AddPlayer(self, Player):
        try:
            self.Players.append(Player)
        except:
            return False
        else:
            self.PlayerCount = len(self.Players)
            return self.PlayerCount
    def UpdatePlayerCount(self):
        self.PlayerCount = len(self.Players)
        return self.PlayerCount
    def RemovePlayer(self, Player):
        removedPlayer = False
        for player in self.Players:
            if Player == player:
                print("remove player: " + str(player))
                self.Players.remove(player)
                removedPlayer = True
        return removedPlayer
    def DumpPlayers(self):
        return self.Players
    def DumpGames(self):
        return []
class GamesRoom:
    def __init__(self, RoomName):
        self.RoomName = RoomName
        self.Games = []
    def DumpPlayers(self):
        inGamePlayers = []
        for game in self.Games:
            inGamePlayers += game.DumpPlayers()
        return inGamePlayers
    def DumpGames(self):
        inGames = []
        for game in self.Games:
            inGames.append(game)
        return inGames
    def UpdatePlayerCount(self):
        inGamePlayers = 0
        for game in self.Games:
            inGamePlayers += game.UpdatePlayerCount()
        return inGamePlayers
    def AddGame(self, MaxPlayers = 2):
        self.Games.append(Game(hashlib.sha256(str(len(self.Games)).encode()).hexdigest(), MaxPlayers))
    def AddPlayer(self, Player):
        foundGame = False
        while not foundGame:
            for game in self.Games:
                if game.MaxPlayers > len(game.DumpPlayers()):
                    if game.AddPlayer(Player):
                        print("found game")
                        return True
            print("creating game!")
            self.AddGame()
    def RemoveGame(self, Game):
        for game in self.Games:
            if game == Game:
                self.Games.remove(Game)
    def RemovePlayer(self, Player):
        for game in self.Games:
            for player in game.DumpPlayers():
                if player == Player:
                    game.EndGame()
class Game:
    def __init__(self, GameID, MaxPlayers = 2, Rounds = 3):
        self.Players = []
        self.MaxPlayers = MaxPlayers
        self.GameID = GameID
        self.Rounds = Rounds
    def AddPlayer(self, Player):
        if len(self.Players) < self.MaxPlayers:
            self.Players.append(Player)
            if len(self.Players) == self.MaxPlayers:
                print("starting game...")
                start_new_thread(self.GameLoop, ())
            return True
        else:
            return False
    def DumpPlayers(self):
        return self.Players
    def EndGame(self):
        print("Game Finished")
        for player in self.Players:
            for room in rooms:
                if rooms[room].RoomName == WaitingRoomName:
                    rooms[room].AddPlayer(player)
        for room in rooms:
            if rooms[room].DumpGames == self:
                rooms[room].RemoveGame(self)
    def SendToAll(self, headers, body, response = False):
        success = True
        self.recievedResponse = []
        for player in self.Players:
            print(player)
            if response:
                start_new_thread(waitForMultipleRecv, (self, headers, body))
                while len(self.recievedResponse) != self.MaxPlayers:
                    time.sleep(0.5)
            else:
                if not SendPacket(player.Conn, headers, body, response):
                    success = False
        if response:
            return recievedResponse
        else:
            return success
    def GameLoop(self):
        """
        self.gameState = "asking"
        self.playerData = {}
        running = True
        while running and len(self.Players) == self.MaxPlayers:
            gameExists = False
        for room in rooms:
            if rooms[room].DumpGames == Game:
                gameExists = True
        if not gameExists:
            sys.exit()
        if self.gameState == "asking":
            optionNo = 1
            for option in options:
                self.SendToAll([["Type", "Command"], ["Command", "PrintToUser"]], [["Message", str(optionNo) + ": " + str(option["Name"]) + " - beats " + str(option["Beats"]) + " but is defeated by " + str(option["DefeatedBy"])]])
                optionNo += 1
            self.SendToAll([["Type", "Command"], ["Command", "AskUserInput"]], [["Question", "What to you choose?"]], True)
            self.gameState == "processingResponses"
        sys.exit()
        """

        running = True
        roundsRemaining = self.Rounds
        scores = {}
        while running and roundsRemaining > 0:
            print("round")
            roundsRemaining = roundsRemaining - 1
            print("sending options")
            optionNo = 1
            self.SendToAll([["Type", "Command"], ["Command", "PrintToUser"]], [["Message", "Round " + str(self.Rounds - roundsRemaining) + ":"]])
            for option in options:
                optionMessage = str(optionNo) + ": " + options[option]["Name"]
                self.SendToAll([["Type", "Command"], ["Command", "PrintToUser"]], [["Message", optionMessage]])
                optionNo += 1
            print(self.SendToAll([["Type", "Command"], ["Command", "AskUserInput"]], [["Question", "oi"]], True))
        self.EndGame()
        sys.exit()

def waitForMultipleRecv(self, headers, body):
    print("Yeet")
    self.recievedResponse.append(SendPacket(conn, headers, body, True))

class Player:
    def __init__(self, PlayerID, Username, PlayerToken, Conn, Addr):
        self.PlayerID = PlayerID
        self.PlayerHash = hashlib.sha256(str(self.PlayerID).encode()).hexdigest()
        self.Username = Username
        self.PlayerToken = PlayerToken
        self.Conn = Conn
        self.Addr = Addr
        self.AwaitingPingResponse = False
        self.PingTimeout = 0
    def RemoveFromRoom(self):
        for room in rooms:
            roomPlayers = rooms[room].DumpPlayers()
            for player in roomPlayers:
                if player == self:
                    rooms[room].RemovePlayer(player)
    def DisconnectPlayer(self):
        self.RemoveFromRoom()
        Connections.remove([self.Conn, self.Addr])
        SendPacket(self.Conn, [["Type", "Disconnect"]], [[]])
        self.Conn.close()

##define player rooms

rooms = {
    WaitingRoomName: PlayerRoom(WaitingRoomName),
    "Games": GamesRoom("Games")
}

##define connections

Connections = []

##define functions

def MovePlayer(Player, ToRoom):
    movedPlayer = False
    deletedPlayer = False
    for room in rooms:
        if rooms[room].RoomName == ToRoom:
            rooms[room].AddPlayer(Player)
            movedPlayer = True
        for player in rooms[room].DumpPlayers():
            if player == Player and rooms[room].RoomName != ToRoom:
                rooms[room].RemovePlayer(Player)
                removedPlayer = True
    if removedPlayer and movedPlayer:
        return True
    else:
        return False

def SendPacket(conn, headers, body, response = False):
    request = {
        "Headers": {},
        "Body": {}
    }
    for parms in headers:
        if parms:
            request["Headers"][parms[0]] = parms[1]
    for parms in body:
        if parms:
            request["Body"][parms[0]] = parms[1]
    request = json.dumps(request)
    request = request.encode()
    print(request)
    try:
        conn.sendall(request)
    except:
        return False
    if response:
        try:
            responded = conn.recv(4096)
        except:
            quit()
        responded = responded.decode('utf-8').strip("\r \n")
        if responded and responded != "":
            json.loads(responded)
            try:
                responded = json.loads(responded)
            except:
                SendPacket(conn, [["Type", "Error"]], [["ErrorMsg", "Command not JSON"]])
            else:
                if responded["Headers"]["Type"] == "Response":
                    return responded
    else:
        return True
def ClientPingUpdate():
    while True:
        time.sleep(1)
        for pingClient in Connections:
            playerPing = FindPlayerByConn(pingClient[0])
            if playerPing.AwaitingPingResponse:
                playerPing.PingTimeout -= 1
            if playerPing.PingTimeout <= 0 and playerPing.AwaitingPingResponse:
                playerPing.DisconnectPlayer()
def ClientPing():
    while True:
        key = 0
        time.sleep(PlayerTimeout + 1)
        for pingClient in Connections:
            print("pinging: " + str(pingClient[1]))
            playerPing = FindPlayerByConn(pingClient[0])
            playerPing.AwaitingPingResponse = True
            playerPing.PingTimeout = PlayerTimeout
            ##print(SendPacket(pingClient[0], [["Type", "Command"], ["Command", "Ping"]], [["PingTimeout", playerPing.PingTimeout], ["AwaitingPingResponse", playerPing.AwaitingPingResponse]]))
            if not SendPacket(pingClient[0], [["Type", "Command"], ["Command", "Ping"]], [["PingTimeout", playerPing.PingTimeout], ["AwaitingPingResponse", playerPing.AwaitingPingResponse]]):
                playerPing.DisconnectPlayer()
        key += 1
def FindPlayerByConn(conn):
    for room in rooms:
        roomPlayers = rooms[room].DumpPlayers()
        for player in rooms[room].DumpPlayers():
            if player.Conn == conn:
                return player
def findRoom(Room):
    for room in rooms:
        if rooms[room] == Room:
            return rooms[room]
def PlayerCount():
    PlayerCount = 0
    for room in rooms:
        PlayerCount += len(room)
def ThreadedClient(conn, addr):
    threadPlayer = FindPlayerByConn(conn)
    while True:
        try:
            data = conn.recv(4096)
        except:
            quit()
        data = data.decode('utf-8').strip("\r \n")
        if data and data != "":
            json.loads(data)
            try:
                data = json.loads(data)
            except:
                SendPacket(conn, [["Type", "Error"]], [["ErrorMsg", "Command not JSON"]])
            else:
                if data["Headers"]["Type"] == "Response":
                    if data["Headers"]["Command"] == "PingResponse":
                        threadPlayer.AwaitingPingResponse = False
                        print("Ping reply recieved form: " + str(threadPlayer.Addr))
                if data["Headers"]["Type"] == "Command":
                    Command = data["Headers"]["Command"]
                    if Command == "PingStatus":
                        SendPacket(conn, [["Type", "Response"], ["Command", "PingAcknowledge"]], [["PingTimeout", threadPlayer.PingTimeout], ["AwaitingPingResponse", threadPlayer.AwaitingPingResponse]])
                    elif Command == "UpdatePlayerData":
                        if data["Body"]["Username"]:
                            threadPlayer.Username = data["Body"]["Username"]
                    elif Command == "GetPlayerData":
                        SendPacket(conn,[["Type", "Response"], ["Command", "GetPlayerData"]], [["Username", threadPlayer.Username]])
                    elif Command == "GetRoomNames":
                        keys = []
                        for key in rooms.keys():
                            keys.append(key)
                        SendPacket(conn,[["Type", "Response"], ["Command", Command]], [["Rooms", keys]])
                    elif Command == "JoinRoom":
                        if data["Body"]["Room"]:
                            roomExists = False
                            room = data["Body"]["Room"]
                            for key in rooms.keys():
                                if key == room:
                                    roomExists = True
                            if roomExists:
                                if MovePlayer(threadPlayer, room):
                                    SendPacket(conn,[["Type", "Response"], ["Command", Command]], [["Room", data["Body"]["Room"]]])
                                else:
                                    SendPacket(conn,[["Type", "Error"], ["Command", Command]], [["ErrorMsg", "Could not move player"]])
                            else:
                                SendPacket(conn,[["Type", "Error"], ["Command", Command]], [["ErrorMsg", "Room does not exist"]])
                        else:
                            SendPacket(conn,[["Type", "Error"], ["Command", Command]], [["ErrorMsg", "No room set"]])
                    else:
                        SendPacket(conn, [["Type", "Error"], ["Command", Command]], [["ErrorMsg", "Command not found"]])


if __name__ == '__main__':
    start_new_thread(ClientPing, ())
    start_new_thread(ClientPingUpdate, ())
    while True:
        conn, addr  = s.accept()
        Connections.append([conn, addr])
        rooms["WaitingRoom"].AddPlayer(Player(PlayerCount(), "", "", conn, addr))
        start_new_thread(ThreadedClient, (conn, addr))
