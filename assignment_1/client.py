from socket import *
serverName = 'localhost'
serverPort = 6000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
sentence = 'Input lowercase sentence'
clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(1024)
print('Frame Server: ', modifiedSentence.decode())
clientSocket.close()
