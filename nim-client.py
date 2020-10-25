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
        while len(byteStep) != 0:
            ret = clientSoc.send(byteStep)
            byteStep = byteStep[ret:]
    except OSError as error:
        print(error.strerror)
        return False
    return True


def myRecvall(clientSoc, expectedLenInBytes):
    gotSize = 0
    chunks = []
    while gotSize < expectedLenInBytes:
        try:
            data = clientSoc.recv(1024)
        except OSError as error:
            if error.errno == errno.ECONNREFUSED:
                print("disconnect from sever server")
            else:
                print(error.strerror + ", cannot start playing")
        if data == b'':
            print("Disconnected from server")
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
            return False, struct.pack(">ci", b'Z', 0)
        else:
            return False, struct.pack(">ci", splitStep[0].encode(UTF), int(splitStep[1]))
    elif len(splitStep) == 1:
        if splitStep[0] == "Q":
            return True, struct.pack(">ci", b'Q', 0)
        else:
            return False, struct.pack(">ci", b'Z', 0)
    else:
        return False, struct.pack(">ci", b'Z', 0)


# returns True if play is not over, otherwise returns False
def parseCurrentPlayStatus(data):
    tav, nA, nB, nC = struct.unpack(">ciii", data)
    print(f"tav {tav}")
    if tav == b'i':
        print("nim")
    elif tav == b'g' or tav == b's' or tav == b'c':
        print("Move accepted")
    elif tav == b'x' or tav == b't':
        print("Illegal move")

    print("Heap A: " + str(nA))
    print("Heap B: " + str(nB))
    print("Heap C: " + str(nC))

    if tav == b's' or tav == b't':
        print("Server win!")
        return False
    elif tav == b'c':
        print("You win!")
        return False
    print("Your turn:")
    return True


# while game on and connection is valid, get the heap status, and send the new game move
def startPlay(clientSoc):
    run = True
    while run:
        run, allDataRecv = myRecvall(clientSoc, 13)
        if run and sys.getsizeof(allDataRecv) - STRUCT_SIZE == 13:
            run = parseCurrentPlayStatus(allDataRecv)
            if run:
                quitCommand, bytesNewMove = createStep()
                if not quitCommand:
                    print(f'bytes to send: {bytesNewMove}')
                    run = mySendall(clientSoc, bytesNewMove)
                else:
                    run = False
        elif run:
            print("invalid data received from server")
            run = False


# create the first connection
def connectToGame(hostName, port):
    clientSoc = None
    try:
        clientSoc = socket(AF_INET, SOCK_STREAM)
        clientSoc.connect((hostName, port))
        startPlay(clientSoc)
    except OSError as error:
        if error.errno == errno.ECONNREFUSED:
            print("connection refused by server")
        else:
            print(error.strerror + ", cannot start playing")
    finally:
        if clientSoc is not None:
            clientSoc.close()


def main():
    n = len(sys.argv)
    hostName = ""
    port = "6444"
    if n > 2:
        hostName = sys.argv[1]
        port = sys.argv[2]
    elif n > 1:
        hostName = sys.argv[1]
    if port.isdigit():
        connectToGame(hostName, int(port))
    else:
        print("second argument is not a valid port number, cannot start playing")


main()