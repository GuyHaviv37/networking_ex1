#!/usr/bin/python3

import errno
import struct
import sys
import socket
from socket import AF_INET, socket, SOCK_STREAM

STRUCT_SIZE = 33
UTF = 'utf-8'


def mySendall(clientSoc, byteStep):
    try:
        while len(byteStep != 0):
            ret = clientSoc.send(byteStep)
            byteStep = byteStep[ret:]
    except socket.error as error:
        print(error.strerror)
        return False
    return True


def myRecvall(clientSoc, expectedLenInBytes):
    gotSize = 0
    chunks = []
    while gotSize < expectedLenInBytes:
        data = clientSoc.recv(1024)
        # check the difference from data == b''
        if data == 0:
            print("Disconnected from server\n")
            return False, b''
        gotSize += sys.getsizeof(data) - STRUCT_SIZE
        chunks.append(data)
    return True, b''.join(chunks)


# returns bytes object with the data to send to the server- format ">ci"
def createStep():
    step = input()
    splitStep = step.split()
    if len(splitStep) == 2:
        if splitStep[0] == "Q" or len(splitStep[0]) != 1 or not splitStep[1].isdigit():
            return struct.pack(">ci", b'Z', 0)
        else:
            return struct.pack(">ci", splitStep[0].encode(UTF), int(splitStep[1]))
    elif len(splitStep) == 1:
        if splitStep[0] == "Q":
            return struct.pack(">ci", b'Q', 0)
    else:
        return struct.pack(">ci", b'Z', 0)


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
        print("Server win!")
        return False
    elif tav == "c":
        print("You win!")
        return False
    print("Heap A: " + str(nA) + "\n")
    print("Heap B: " + str(nB) + "\n")
    print("Heap C: " + str(nC) + "\n")
    print("Your turn:\n")
    return True


# while game on and connection is valid, get the heap status, and send the new game move
def startPlay(clientSoc):
    run = True
    while run:
        run, allDataRecv = myRecvall(clientSoc, 13)
        if run and sys.getsizeof(allDataRecv) - STRUCT_SIZE == 13:
            run = parseCurrentPlayStatus(allDataRecv)
            if run:
                bytesNewMove = createStep()
                run = mySendall(clientSoc, bytesNewMove)
        elif run:
            print("invalid data received from server")
            run = False


# create the first connection
def connectToGame(hostName, port):
    clientSoc = socket(AF_INET, SOCK_STREAM)
    try:
        clientSoc.connect((hostName, port))
        startPlay(clientSoc)
    except OSError as error:
        if error.errno == errno.ECONNREFUSED:
            print("connection refused by server")
        else:
            print(error.strerror + ", cannot start playing")
    finally:
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
