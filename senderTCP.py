import pickle
import random
from socket import *
from time import sleep


def makepkt(Field1, Field2, Field3):
    return {0: Field1, 1: Field2, 2: Field3}


def randInRange(minR, maxR, default):
    val = random.random()
    if minR < val <= maxR:
        return val
    return default


def recvThenSendWithTimeoutHandler():  # AUTO HANDLER FOR PACKET LOST TIMEOUT EVENTS
    try:
        receivedHandler = clientSocket.recv(packetSize)
        return pickle.loads(receivedHandler)
    except timeout:
        print(f"ACK {toSend[1]} timeout timer expired (packet lost)", "\n")
        print(f"A packet with sequence number {toSend[1]} is about to be resent ")
        print(f"Packet to send contains: data = {toSend[0]}, seq = {toSend[1]}, isack = {toSend[2]}")
        print(f"Starting timeout timer for ACK {toSend[1]}\n")
        clientSocket.send(toSendEncoded)
        return recvThenSendWithTimeoutHandler()


serverName = 'localhost'
serverPort = 50007
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
sequenceNumber = 0
packetSize = len(pickle.dumps(makepkt(0, 0, False))) + 1

# random.seed(random.randrange(2, 32000, 1))
packetsToSend = random.randrange(1, 100, 1)
# packetsToSend = 10


for i in range(packetsToSend):

    print(f"The sender is moving to state WAIT FOR CALL {sequenceNumber} FROM ABOVE\n")

    # random.seed(randInRange(2, 32000, 111))
    sleep(random.uniform(0, 6))

    # random.seed(randInRange(2, 32000, 333))
    data = int(random.randrange(2, 32000, 1))
    # data = i + 1

    toSend = makepkt(data, sequenceNumber, False)
    toSendEncoded = pickle.dumps(toSend)

    # print(len(toSendEncoded))

    print(f"A packet with sequence number {toSend[1]} is about to be sent ")
    print(f"Packet to send contains: data = {toSend[0]}, seq = {toSend[1]}, isack = {toSend[2]}")
    clientSocket.send(toSendEncoded)

    print(f"Starting timeout timer for ACK {toSend[1]}\n")
    roundTripTravel = randInRange(3, 10, 5)
    clientSocket.settimeout(roundTripTravel)

    print(f"The sender is moving to state WAIT FOR ACK{toSend[1]}\n")

    decoded = recvThenSendWithTimeoutHandler()

    # random.seed(randInRange(2, 32000, 222))
    ackCorrupted = randInRange(0, 1, 0.001)
    ackLost = randInRange(0, ackCorrupted, 0.0005)
    ackProbability = randInRange(0, 1, 0.0005)

    while ackProbability < ackLost or ackLost < ackProbability < ackCorrupted:  # iTH PACKET LOOP

        if ackProbability < ackLost:    # ACK LOST for this end. If lost on receiver end, then
                                        # recvThenSendWithTimeoutHandler() takes care of it
            print(f"ACK {toSend[1]} timeout timer expired (ACK lost)", "\n")
            print(f"A packet with sequence number {toSend[1]} is about to be resent ")
            print(f"Packet to send contains: data = {toSend[0]}, seq = {toSend[1]}, isack = {toSend[2]}")
            print(f"Starting timeout timer for ACK {toSend[1]}\n")

            print(f"The sender is moving back to state WAIT FOR ACK{toSend[1]}\n")

            decoded = recvThenSendWithTimeoutHandler()

        if ackLost < ackProbability < ackCorrupted:  # ACK CORRUPTED
            print("A Corrupted ACK packet has just been received")

            print(f"The sender is moving back to state WAIT FOR ACK{toSend[1]}\n")

            # print(f"A packet with sequence number {toSend[1]} is about to be resent ")
            # print(f"Packet to send contains: data = {toSend[0]}, seq = {toSend[1]}, isack = {toSend[2]}")
            # print(f"Starting timeout timer for ACK {toSend[1]}\n")
            decoded = recvThenSendWithTimeoutHandler()

        # random.seed(randInRange(2, 32000, 222))
        ackCorrupted = randInRange(0, 1, 0.001)
        ackLost = randInRange(0, ackCorrupted, 0.0005)
        ackProbability = randInRange(0, 1, 0.0005)

    if decoded[1] != toSend[1]:  # DUPLICATE ACK RECEIVED
        print(f"A duplicate ACK {decoded[1]} packet has just been received")
        print(f"Packet received contains: data = {decoded[0]} seq = {decoded[1]} isack = {decoded[2]}")

        print(f"The sender is moving back to state WAIT FOR ACK{toSend[1]}\n")

        # print(f"A packet with sequence number {toSend[1]} is about to be resent ")
        # print(f"Packet to send contains: data = {toSend[0]}, seq = {toSend[1]}, isack = {toSend[2]}")
        # print(f"Starting timeout timer for ACK {toSend[1]}\n")
        decoded = recvThenSendWithTimeoutHandler()

    # ACK RECEIVED SUCCESSFULLY
    print(f"An ACK {decoded[1]} packet has just been received ")
    print(f"Packet received contains: data = {decoded[0]} seq = {decoded[1]} isack = {decoded[2]}")
    print(f"Stopping timeout timer for ACK {toSend[1]}\n")

    if sequenceNumber == 0:
        sequenceNumber = 1
    else:
        sequenceNumber = 0
