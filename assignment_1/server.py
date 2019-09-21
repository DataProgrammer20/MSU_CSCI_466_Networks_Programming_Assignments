import sys as system
from http.server import *


class BattleshipServer(BaseHTTPRequestHandler):
    port = 0
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

    @classmethod
    def run(cls, port=5000, client_board_file=''):
        cls.port = int(port)
        cls.client_board_file = client_board_file
        # Starting server
        server_address = ('127.0.0.1', cls.port)
        httpd = HTTPServer(server_address, BattleshipServer)
        print('Server is listening on IP: 127.0.0.1, ' + 'port: ' + str(cls.port))
        print('Parsing client board...')
        cls.parse_client_board(cls)
        print('Awaiting client connections...')
        httpd.serve_forever()

    def do_GET(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send message back to client
        message = "Welcome to the Battleship server!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    def do_POST(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send message back to client
        message = "You fired your cannon!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

BattleshipServer.run(system.argv[1], system.argv[2])
