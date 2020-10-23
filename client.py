#!/usr/bin/python3

import errno
import struct
import sys
from socket import AF_INET, socket, SOCK_STREAM


def mySendall(sock, byteStep):
    try:
        while len(byteStep != 0):
            ret = sock.send(byteStep)
            byteStep = byteStep[ret:]
    except socket.error as error:
        print(error.strerror)
        return False
    return True


# returns bytes object with the data to send to the server- format ">ci"
def createStep():
    step = input()
    splitStep = step.split()
    if len(splitStep) == 2:
        if splitStep[0] == "Q":
            return struct.pack(">ci", "Z", 0)
        else:
            return struct.pack(">ci", splitStep[0], splitStep[1])
    elif len(splitStep) == 1:
        if splitStep[0] == "Q":
            return struct.pack(">ci", "Q", 0)
    else:
        return struct.pack(">ci", "Z", 0)


# returns True if play is not over, otherwise returns False
def parseCurrentPlayStatus(data):
    tav, nA, nB, nC = struct.unpack(">ciii", data)
    if tav == "i":
        print("nim\n")
    elif tav == "g":
        print("Move accepted\n")
    elif tav == "x":
        print("Illegal move\n")
    elif tav == "s":
        print("Server win!\n")
        return False
    elif tav == "c":
        print("You win!\n")
        return False
    print("Heap A: " + str(nA) + "\n")
    print("Heap B: " + str(nB) + "\n")
    print("Heap C: " + str(nC) + "\n")
    print("Your turn:\n")
    return True


def startPlay(clientSoc):
    run = True
    while run:
        data = clientSoc.recv(1024)
        if data == 0:
            print("Disconnected from server\n")
            run = False
        else:
            run = parseCurrentPlayStatus(data)
            if run:
                byteStep = createStep()
                run = mySendall(clientSoc, byteStep)


def connectToGame(hostName, port):
    clientSoc = socket(AF_INET, SOCK_STREAM)
    try:
        clientSoc.connect((hostName, port))
        startPlay(clientSoc)
        clientSoc.close()
    except OSError as error:
        if error.errno == errno.ECONNREFUSED:
            print("connection refused by server")
        else:
            print(error.strerror + ", cannot start playing")
        clientSoc.close()


def main():
    n = len(sys.argv)
    hostName = ""
    port = 6444
    if n > 2:
        hostName = sys.argv[1]
        port = sys.argv[2]
    elif n > 1:
        hostName = sys.argv[1]
    connectToGame(hostName, port)
