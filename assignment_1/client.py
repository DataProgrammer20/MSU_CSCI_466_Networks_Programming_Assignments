from socket import *
import sys as system


class BattleshipClient:
    ip = 0
    port = 0
    x = 0
    y = 0
    client_socket = ''

    def __init__(self, ip="127.0.0.1", port=5000, x=0, y=0):

        # Debugging values
        print("Command line values: ", ip, port, x, y)
        # ================

        self.ip = ip
        self.port = int(port)
        self.x = int(x)
        self.y = int(y)
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))

        command = 'fire ' + str(self.x) + ' ' + str(self.y)

        # sending message
        self.client_socket.send(command.encode())

        # response
        modified_sentence = self.client_socket.recv(1024)

        print('Server Response: ', modified_sentence.decode())

        self.client_socket.close()

client = BattleshipClient(
    system.argv[1],
    system.argv[2],
    system.argv[3],
    system.argv[4]
)
