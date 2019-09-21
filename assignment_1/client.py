from socket import *
import sys as system


class BattleshipClient:
    ip = 0
    port = 0
    x = 0
    y = 0
    client_socket = ''

    def __init__(self, ip="127.0.0.1", port=6000, x=0, y=0):

        # Debugging values
        print("Command line values: ", ip, port, x, y)
        # ================

        self.ip = ip
        self.port = port
        self.x = x
        self.y = y
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))
        sentence = 'hello from client town'
        self.client_socket.send(sentence.encode())
        modified_sentence = self.client_socket.recv(1024)
        print('Server Response: ', modified_sentence.decode())
        self.client_socket.close()

client = BattleshipClient(
    system.argv[1],
    system.argv[2],
    system.argv[3],
    system.argv[4]
)
