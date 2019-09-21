from http.client import *
import sys as system


class BattleshipClient:
    ip = 0
    port = 0
    x = 0
    y = 0
    client_socket = ''

    def __init__(self, ip="127.0.0.1", port=5000, x=0, y=0):
        self.ip = ip
        self.port = int(port)
        self.x = int(x)
        self.y = int(y)

        connection = HTTPConnection(self.ip, self.port)
        print(connection)
        connection.request("GET", "/")
        response = connection.getresponse()
        print("Status: ", response.status)

client = BattleshipClient(
    system.argv[1],
    system.argv[2],
    system.argv[3],
    system.argv[4]
)
