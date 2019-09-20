from socket import *
serverPort = 6000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is online and ready to receive')
while True:
    connectionSocket, address = serverSocket.accept()
    print('Got a client at: ' + str(address))
    sentence = connectionSocket.recv(1024).decode()
    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence.encode())
    connectionSocket.close()
