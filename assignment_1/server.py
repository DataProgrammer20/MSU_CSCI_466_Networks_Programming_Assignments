from socket import *
import sys as system


class BattleshipServer:
    port = 6000
    board_file = ''

    def __init__(self, port=6000, board_file=''):
        self.port = int(port)
        self.board_file = board_file

        # Debugging
        print('port and board file values: ', self.port, self.board_file)
        # ===========

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(1)
        print('Server is listening on IP: 127.0.0.1, ' + 'port: ' + str(self.port))
        print('Starting connection handler...')
        self.handler(server_socket)

    @staticmethod
    def handler(server_socket=None):
        print('Waiting for connections...')
        while True:
            client_socket, address = server_socket.accept()
            print('Got a client at: ' + str(address))
            sentence = client_socket.recv(1024).decode()
            capitalized_sentence = sentence.upper()
            client_socket.send(capitalized_sentence.encode())
            client_socket.close()


server = BattleshipServer(system.argv[1], system.argv[2])
