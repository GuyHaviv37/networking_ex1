#!/usr/bin/python3
import socket
import struct
import sys

# Gets command line input
# returns - N_a,N_b,N_c[,PORT]
# TESTED
def getConsoleInput():
    inputLen = len(sys.argv)
    if not(inputLen == 4  or inputLen==5) :
        print("Invalid number of arguements for nim-server")
        print("Should be 3/4 : heapA heapB heapC [PORT]")
        sys.exit(0)
    na = sys.argv[1]
    nb = sys.argv[2]
    nc = sys.argv[3]
    if(inputLen == 5): # can add check to viable PORT number , i.e. > 1024
        port = sys.argv[4]
    else:
        port = 6444
    return na,nb,nc,port

# Gets char as heapId
# 'A'/'B'/'C' returns 0,1,2 respectivly.
# 'Q' return 3
# Any other heapId (invalid) returns -1 
def parseHeapId(heapId):
    return {
        'A' : 0,
        'B' : 1,
        'C' : 2,
        'Q' : 3
    }.get(heapId,-1)

# Checks if current client move is valid
# 0 <= heapIndex <=2 && heaps[heapIndex] >= amount
# returns boolean
# TESTED
def checkValid(heaps,heapIndex,amount):
    if(heapIndex < 0 or heapIndex > 2):
        return False
    if(heaps[heapIndex] >= amount):
        return True
    else:
        return False
    
# Makes server game move
# Looks for biggest heap and removes 1 from it
# TESTED
def updateHeapsServer(heaps):
    maxNum = max(heaps)
    for i in range(3):
        if heaps[i] == maxNum:
            heaps[i] -= 1
            break

# Makes client game move
# available only if checkValid returns True on params
# TESTED
def updateHeapsClient(heaps,heapIndex,amount):
    heaps[heapIndex] -= amount

# Checks if game was won
# TESTED
def checkForWin(heaps):
    return True if sum(heaps) <= 0 else False

# Main server function
def server(na,nb,nc,PORT):
    listenSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print("Socket created successfully")

    listenSocket.bind(('',PORT))
    print("Bind was done successfully")

    listenSocket.listen(1)
    print("Listen was done successfully")
    while True:
        conn , addr = listenSocket.accept()
        #Initialize game
        init = True
        gameOver = False
        heaps = [na,nb,nc]
        messageTag = 'i'
        dataSent = struct.pack(">chhh",messageTag,heaps[0],heaps[1],heaps[2])
        while(not gameOver):
            if init == True: # send with 'i' tag
                conn.send(dataSent)
                init = False
            else: # send with messageTag
                dataSent = struct.pack(">ciii",messageTag,heaps[0],heaps[1],heaps[2])
                conn.send(dataSent)
            #receive message from client
            bytesRecv = conn.recv(5) # 1 char and 1 int
            dataRecv = struct.unpack(">ci",bytesRecv)
            #parse message from client
            heapId , amount = dataRecv
            heapIndex = parseHeapId(heapId) 
            if(heapIndex >= 3): # Quit program
                break
            # Make game move and set messageTag:
            if(not checkValid(heaps,heapIndex,amount)):
                messageTag = 'x'
                updateHeapsServer(heaps)
                if(checkForWin(heaps) == True):
                    messageTag = 's'
            else:
                messageTag = 'g'
                updateHeapsClient(heaps,heapIndex,amount)
                if(checkForWin(heaps) == True):
                    messageTag = 'c'
                else:
                    updateHeapsServer(heaps)
                    if(checkForWin(heaps) == True):
                        messageTag = 's'
            #continue program with loop
        conn.close()

    listenSocket.close()
    print("ListenSocket was closed successfully")

#Main function for the program
def main():
    print("main")
    na,nb,nc,PORT = getConsoleInput()
    print(na,nb,nc,PORT)
    server(na,nb,nc,PORT)
    # heaps = [5,5,5]
    # while(True):
    #     print(heaps)
    #     index = int(input())
    #     amount = int(input())
    #     updateHeapsClient(heaps,index,amount)
    #     if(checkForWin(heaps)):
    #         print("Client won")
    #         break
    #     updateHeapsServer(heaps)
    #     if(checkForWin(heaps)):
    #         print("Server won")
    #         break



main()