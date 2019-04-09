import sys
import json
from socket import *
TAILLE_TAMPON =1024

class Client:
    def __init__(self, ipServ, portServ):
        self.sock = socket()
        self.sock.connect((ipServ, portServ))

    def connectionRequest(self,pseudo):
        request = {
            "pseudo": pseudo,
            "exchange": "login"
        }
        self.sendRequest(request)
        return self.waitAwnser()

    def placementRequest(self, coord):
        request = {
            "exchange":"placement",
            "data":[coord[0],coord[1]]
        }
        self.sendRequest(request)
        return self.waitAwnser()

    def moveRequest(self, direction):
        request = {
            "exchange":"move",
            "data":direction
        }
        self.sendRequest(request)
        return self.waitAwnser()
    def refreshRequest(self):
        request = {
            "exchange": "refresh"
        }
        self.sendRequest(request)
        awnser = self.waitAwnser()
        if awnser["code"] ==200 :
            return awnser["data"]
        else:
            print("Mauvais code" + str(awnser["code"]))


    def refreshPlayer(self):
        request = {
            "exchange": "listof"
        }
        self.sendRequest(request)
        awnser = self.waitAwnser()
        return awnser["data"]


    def logoutRequest(self):
        request = {
            "exchange": "logout"
        }
        self.sendRequest(request)
        awnser = self.waitAwnser()
        self.sock.close()
        return awnser

    def modRequest(self, newPseudo):
        request = {
            "exchange": "mod",
            "data":newPseudo
        }
        self.sendRequest(request)
        return self.waitAwnser()

    def pauseRequest(self):
        request = {
            "exchange": "pause"
        }
        self.sendRequest(request)
        return self.waitAwnser()

    def continueRequest(self):
        request = {
            "exchange": "continue"
        }
        self.sendRequest(request)
        return self.waitAwnser()
    

    def sendRequest(self, request):
        request = json.dumps(request)
        request = request.encode()
        self.sock.send(request)


    def waitAwnser(self):
        awnser = self.sock.recv(1024)
        awnser = json.loads(awnser)
        return awnser