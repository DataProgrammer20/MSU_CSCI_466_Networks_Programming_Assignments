import sys as system
import random
import urllib.parse as urlparse
from http.server import *


class BattleshipServer(BaseHTTPRequestHandler):
    port = 0
    client_board_file = ''
    server_board_file = 'opponent_board.txt'
    client_ship_count = 5
    server_ship_count = 5
    server_victory = False
    client_victory = True
    server_tokens = {'C': 5, 'B': 4, 'R': 3, 'S': 3, 'D': 2}
    client_tokens = {'C': 5, 'B': 4, 'R': 3, 'S': 3, 'D': 2}
    client_board = []
    server_board = []

    # def server_turn(self):

    def get_server_file_content(self):
        file = open('opponent_board.txt', 'r')
        character = file.readline(1)
        line = ''
        file_content = ''
        char_count = 0
        while character:
            if char_count == 10:
                file_content += line + '<br>'
                line = ''
                char_count = 0
            if (character == 'C' or character == 'R' or character == 'D' or character == 'B' or character == 'S'):
                line += '_'
                character = file.readline(1)
                char_count += 1
            elif character == '\n':
                character = file.readline(1)
                continue
            else:
                line += character
                character = file.readline(1)
                char_count += 1
        return file_content

    def get_client_file_content(self):
        file = open('own_board.txt', 'r')
        line = file.readline()
        file_content = ''
        while line:
            file_content += line + '<br>'
            line = file.readline()
        return file_content

    def save_to_file(self, type, board):
        file = ''
        if type == 'client':
            file = self.client_board_file
        else:
            file = self.server_board_file
        open(file, 'w').close()
        file_append = open(file, 'a')
        line = ''
        for row in board:
            for character in row:
                line += character
            file_append.write(line + '\n')
            line = ''
        file_append.close()

    def check_victory(self, ship_count, player):
        result = [False, '']
        if ship_count == 0:
            result[0] = True
            result[1] = "The " + player + " has won the game!"
            return result
        return result

    def send_http_response(self, status, headers, message):
        self.send_response(status)
        self.send_header(headers[0], headers[1])
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))

    def parse_board(self, type):
        board_line = []
        if type == 'client':
            client_file = open(self.client_board_file, 'r')
            file_line = client_file.readline()
            while file_line:
                for index in range(0, 10):
                    character = file_line[index]
                    board_line.append(character)
                self.client_board.append(board_line)
                board_line = []
                file_line = client_file.readline()
            client_file.close()
        else:
            server_file = open(self.server_board_file, 'r')
            file_line = server_file.readline()
            while file_line:
                for index in range(0, 10):
                    character = file_line[index]
                    board_line.append(character)
                self.server_board.append(board_line)
                board_line = []
                file_line = server_file.readline()
            server_file.close()

    @classmethod
    def run(cls, port=5000, client_board_file=''):
        cls.port = int(port)
        cls.client_board_file = client_board_file
        # Starting server
        server_address = ('127.0.0.1', cls.port)
        httpd = HTTPServer(server_address, BattleshipServer)
        print('Server is listening on IP: 127.0.0.1, ' + 'port: ' + str(cls.port))
        print('Parsing client board...')
        cls.parse_board(cls, 'client')
        print('Parsing server board...')
        cls.parse_board(cls, 'server')
        print('Awaiting client connections...')
        httpd.serve_forever()

    def do_GET(self):
        if self.path == '/own_board.html':
            file_content = self.get_client_file_content()
            DOM = '<div style="margin: 100px auto; text-align: left; width: 100px;">' + file_content + '</div>'
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(DOM, 'utf8'))
            return

        elif self.path == '/opponent_board.html':
            file_content = self.get_server_file_content()
            DOM = '<div style="margin: 100px auto; text-align: left; width: 100px;">' + file_content + '</div>'
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(DOM, 'utf8'))
            return

        else:
            self.send_response(200)
            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Send message back to client
            message = "Welcome to the Battleship server!"
            # Write content as utf-8 data
            self.wfile.write(bytes(message, 'utf8'))
            return

    def do_POST(self):
        status = 0
        message = ''
        headers = []
        sink = ''
        url = self.path
        parsed_url = urlparse.urlparse(url)
        y_coord = int(urlparse.parse_qs(parsed_url.query)['y'][0])
        x_coord = int(urlparse.parse_qs(parsed_url.query)['x'][0])
        game_over = self.check_victory(self.server_ship_count, 'client')

        if game_over[0]:
            status = 200
            headers.append('URL')
            headers.append('127.0.0.1:5000')
            self.send_http_response(status, headers, game_over[1])
            return

        if y_coord > 9 or y_coord < 0 or x_coord > 9 or x_coord < 0:
            status = 404
            headers.append('URL')
            headers.append('127.0.0.1:5000')
            message = 'Values out of range!'

        elif self.server_board[y_coord][x_coord] == 'C' or self.server_board[y_coord][x_coord] == 'B' or self.server_board[y_coord][x_coord] == 'R' or self.server_board[y_coord][x_coord] == 'S' or self.server_board[y_coord][x_coord] == 'D':
            key = self.server_board[y_coord][x_coord]
            if self.server_tokens[key] == 1:
                sink = '&sink=' + key
                self.server_ship_count -= 1
            self.server_tokens[key] -= 1
            self.server_board[y_coord][x_coord] = 'X'
            status = 200
            headers.append('URL')
            headers.append('127.0.0.1:5000?hit=1' + sink)
            message = 'You hit a ship!'

        elif self.server_board[y_coord][x_coord] == '_':
            self.server_board[y_coord][x_coord] = 'X'
            status = 200
            headers.append('URL')
            headers.append('127.0.0.1:5000?hit=0')
            message = 'You missed!'

        elif self.server_board[y_coord][x_coord] == 'X':
            status = 410
            headers.append('URL')
            headers.append('127.0.0.1:5000')
            message = 'You already hit that location!'

        else:
            status = 400
            headers.append('URL')
            headers.append('127.0.0.1:5000')
            message = 'Unknown command'

        self.send_http_response(status, headers, message)
        self.save_to_file('server', self.server_board)
        return

BattleshipServer.run(system.argv[1], system.argv[2])
