import signal, sys
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
        return self.waitAnswer()

    def placementRequest(self, coord):
        request = {
            "exchange":"placement",
            "data":[coord[0],coord[1]]
        }
        self.sendRequest(request)
        return self.waitAnswer()

    def moveRequest(self, direction):
        request = {
            "exchange":"move",
            "data":direction
        }
        self.sendRequest(request)
        return self.waitAnswer()

    def refreshRequest(self):
        request = {
            "exchange": "refresh"
        }
        self.sendRequest(request)
        answer = self.waitAnswer()
        if (answer["code"] == 200):
            return answer["data"]
        else:
            return answer

    def refreshPlayer(self):
        request = {
            "exchange": "listof"
        }
        self.sendRequest(request)
        answer = self.waitAnswer()
        return answer["data"]


    def logoutRequest(self):
        request = {
            "exchange": "logout"
        }
        self.sendRequest(request)
        answer = self.waitAnswer()
        self.sock.close()
        return answer

    def modRequest(self, newPseudo):
        request = {
            "exchange": "mod",
            "data":newPseudo
        }
        self.sendRequest(request)
        return self.waitAnswer()

    def pauseRequest(self):
        request = {
            "exchange": "pause"
        }
        self.sendRequest(request)
        return self.waitAnswer()

    def continueRequest(self):
        request = {
            "exchange": "continue"
        }
        self.sendRequest(request)
        return self.waitAnswer()
    

    def sendRequest(self, request):
        request = json.dumps(request)
        request = request.encode()
        self.sock.send(request)


    def waitAnswer(self):
        answer = self.sock.recv(1024)
        answer = json.loads(answer)
        return answer