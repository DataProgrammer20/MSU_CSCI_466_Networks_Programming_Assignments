from socket import *
server_name = 'localhost'
server_port = 6000
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))
sentence = 'input lowercase sentence'
client_socket.send(sentence.encode())
modifiedSentence = client_socket.recv(1024)
print('Server Response: ', modifiedSentence.decode())
client_socket.close()
