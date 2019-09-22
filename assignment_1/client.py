from http.client import *
import sys as system


class BattleshipClient:
    ip = 0
    port = 0
    x = 0
    y = 0
    client_socket = ''

    def __init__(self, ip="127.0.0.1", port=5000, y=0, x=0):
        self.ip = ip
        self.port = int(port)
        self.y = int(y)
        self.x = int(x)

        connection = HTTPConnection(self.ip, self.port)
        connection.request("POST", "http://127.0.0.1:5000?x=" + str(self.x) + "&y=" + str(self.y))
        response = connection.getresponse()
        print("Status: " + str(response.status))
        print("Reason: " + str(response.reason))
        print("Message: " + str(response.read()).replace('b', ''))
        print("URL: " + response.getheader('URL'))

client = BattleshipClient(
    system.argv[1],
    system.argv[2],
    system.argv[3],
    system.argv[4]
)
