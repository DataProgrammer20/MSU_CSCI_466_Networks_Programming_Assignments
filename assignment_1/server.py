import sys as system
import random
import urllib.parse as urlparse
from http.server import *


class BattleshipServer(BaseHTTPRequestHandler):
    port = 0
    client_board_file = ''
    client_board = []
    server_board = [
        ['_', 'C', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', 'C', '_', '_', '_', '_', '_', '_', 'S', '_'],
        ['_', 'C', '_', '_', '_', '_', '_', '_', 'S', '_'],
        ['_', 'C', '_', 'B', 'B', 'B', 'B', '_', 'S', '_'],
        ['_', 'C', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', 'D', '_', '_'],
        ['_', 'R', 'R', 'R', '_', '_', '_', 'D', '_', '_'],
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
        url = self.path
        # print(url)
        parsed_url = urlparse.urlparse(url)
        # print(parsed_url)
        y_coord = int(urlparse.parse_qs(parsed_url.query)['y'][0])
        x_coord = int(urlparse.parse_qs(parsed_url.query)['x'][0])
        # print(y_coord, x_coord)
        

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
