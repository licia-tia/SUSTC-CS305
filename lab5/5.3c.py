from socket import *
serverName = '127.0.0.1'
serverPort = 53
while True:
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    message = input()
    clientSocket.sendto(message.encode(), (serverName, serverPort))
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    print(modifiedMessage.decode())
    clientSocket.close()
