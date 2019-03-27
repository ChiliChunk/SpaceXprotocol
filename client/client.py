import sys
import json
from socket import *

class Client:
    def __init__(self, ipServ, portServ):
        self.sock = socket()
        self.sock.connect(ipServ, portServ)

    def connectionRequest(self,pseudo):
        request = {
            "pseudo": pseudo,
            "exchange": "login",
        }
        self.sendRequest(request)

    def placementRequest(self, coord):
        request = {
            "exchange":"placement",
            "data":
                {"position":
                     [coord[0],coord[1]]
                 }
        }
        self.sendRequest(request)

    def logoutRequest(self):
        request = {
            "exchange": "logout",
        }
        self.sendRequest(request)
        self.sock.close()


    def sendRequest(self, request):
        request = json.dumps(request)
        request = request.encode()
        socket.send(request)



if __name__ == "main":
    ...
        # Create a new thread for each new request send to the server

        # Une thread ouverte en permanence pour la reception de message
