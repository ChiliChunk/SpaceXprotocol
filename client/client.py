import sys
import json
from socket import *
TAILLE_TAMPON =256

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
            "data":
                {"position":
                     [coord[0],coord[1]]
                 }
        }
        self.sendRequest(request)
        return self.waitAwnser()


    def logoutRequest(self):
        request = {
            "exchange": "logout"
        }
        self.sendRequest(request)
        awnser = self.waitAwnser()
        self.sock.close()
        return awnser


    def sendRequest(self, request):
        request = json.dumps(request)
        request = request.encode()
        self.sock.send(request)

    def waitAwnser(self):
        awnser = self.sock.recv(TAILLE_TAMPON).decode()
        #print("awnser : " + awnser )
        awnser = json.loads(awnser)
        return awnser




if __name__ == "__main__":
    c1 = Client("127.0.0.1", 12345)
    c1.connectionRequest("ZOUGLOU31")
    c1.placementRequest([3,3])
    c1.sock.close()

    # Create a new thread for each new request send to the server

    # Une thread ouverte en permanence pour la reception de message
