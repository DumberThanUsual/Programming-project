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

HEADER = 64

Clients = []

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

def ClientConnectionListener(conn, addr):
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
            else:
                print("[ClientConnectionListener] - Disconnecting - " + addr[0] + ":" + str(addr[1]) + " closed the connection")
                connected = False
    conn.close()
    print("[ClientConnectionListener] - Disconnected - " + addr[0] + ":" + str(addr[1]))

while True:
    conn, addr  = s.accept()
    print("[LISTENER]Connection from: " + str(addr))
    thread = threading.Thread(target=ClientConnectionListener, args=(conn, addr))
    thread.start()
