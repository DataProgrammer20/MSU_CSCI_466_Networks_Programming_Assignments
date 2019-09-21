from socket import *
import sys as system


class BattleshipServer:
    port = 6000
    client_board_file = ''
    client_board = []
    server_board = [
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_']
    ]

    def __init__(self, port=6000, board_file=''):
        self.port = int(port)
        self.client_board_file = board_file

        # Debugging
        print('port and board file values: ', self.port, self.client_board_file)
        # ===========

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(1)
        print('Server is listening on IP: 127.0.0.1, ' + 'port: ' + str(self.port))
        print('Parsing client board...')
        self.parse_client_board()
        print('Starting connection handler...')
        self.handler(server_socket)

    def handler(self, server_socket=None):
        print('Waiting for connections...')
        while True:
            client_socket, address = server_socket.accept()
            print('Got a client at: ' + str(address))
            sentence = client_socket.recv(1024).decode()
            capitalized_sentence = sentence.upper()
            client_socket.send(capitalized_sentence.encode())
            client_socket.close()

    def parse_client_board(self):
        client_file = open(self.client_board_file, 'r')
        board_line = []
        file_line = client_file.readline()
        while file_line:
            for index in range(0, 10):
                character = file_line[index]
                board_line.append(character)
            self.client_board.append(board_line)
            board_line = []
            file_line = client_file.readline()
        client_file.close()

server = BattleshipServer(system.argv[1], system.argv[2])
