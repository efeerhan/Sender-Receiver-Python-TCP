import pickle
import random
from socket import *


def makepkt(Field1, Field2, Field3):
    return {0: Field1, 1: Field2, 2: Field3}


def randInRange(minR, maxR, default):
    val = random.random()
    if minR < val <= maxR:
        return val
    return default


serverHost = ''
serverPort = 50007
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverHost, serverPort))
serverSocket.listen(1)
lastReceived = makepkt(0, 1, False)
rec_data = []
packetSize = len(pickle.dumps(makepkt(0, 0, False))) + 1
connectionID, addr = serverSocket.accept()

print("The receiver is moving to state WAIT FOR 0 FROM BELOW\n")

while True:
    try:

        received = connectionID.recv(packetSize)
        decoded = pickle.loads(received)

        # print(len(received))
        random.seed(randInRange(2, 32000, 555))
        packetCorrupted = randInRange(0, 1, 0.001)
        packetLost = randInRange(0, packetCorrupted, 0.0005)

        random.seed(random.randrange(2, 32000, 1))
        packetProbability = random.uniform(0, 1)

        if packetLost < packetProbability or packetCorrupted < packetProbability:   # PACKET DELIVERED

            if decoded[1] == lastReceived[1]:   # DUPLICATE PACKET RECEIVED
                print(f"A duplicate packet with sequence number {decoded[1]} has just been received ")
                toSend = makepkt(0, lastReceived[1], True)
                print(f"Packet received contains: data = {decoded[0]} seq = {decoded[1]} isack= {decoded[2]}")
                print(f"ACK packet to send contains: data = {toSend[0]} seq = {toSend[1]} isack= {toSend[2]}\n")

                if decoded[1]:
                    print("The receiver is moving back to state WAIT FOR 0 FROM BELOW\n")
                else:
                    print("The receiver is moving back to state WAIT FOR 1 FROM BELOW\n")

            else:
                print(f"A packet with sequence number {decoded[1]} has just been received ")
                lastReceived = decoded
                rec_data.append(lastReceived)
                toSend = makepkt(0, lastReceived[1], True)
                print(f"Packet received contains: data = {decoded[0]} seq = {decoded[1]} isack= {decoded[2]}")
                print(f"ACK packet to send contains: data = {toSend[0]} seq = {toSend[1]} isack= {toSend[2]}\n")

                if decoded[1]:
                    print("The receiver is moving to state WAIT FOR 0 FROM BELOW\n")
                else:
                    print("The receiver is moving to state WAIT FOR 1 FROM BELOW\n")

            toSendEncoded = pickle.dumps(toSend)
            connectionID.send(toSendEncoded)

        if packetLost < packetProbability < packetCorrupted:    # PACKET CORRUPTED
            print("A Corrupted package has just been received")
            toSend = makepkt(0, lastReceived[1], True)
            toSendEncoded = pickle.dumps(toSend)
            print(f"ACK packet to send contains: data = {toSend[0]} seq = {toSend[1]} isack= {toSend[2]}\n")

            if decoded[1]:
                print("The receiver is moving back to state WAIT FOR 0 FROM BELOW\n")
            else:
                print("The receiver is moving back to state WAIT FOR 1 FROM BELOW\n")

            connectionID.send(toSendEncoded)

        if packetProbability < packetLost:  # PACKET LOST
            print("A packet has been lost\n")
            if decoded[0]:
                print("The receiver is moving back to state WAIT FOR 0 FROM BELOW\n")
            else:
                print("The receiver is moving back to state WAIT FOR 1 FROM BELOW\n")

        # print("Received Data So Far:")
        # for x in rec_data:
        #     print(x[0])

    except (IOError, EOFError) as e:
        pass
