import signal, sys
import json
from socket import *
TAILLE_TAMPON =1024

class Client:
    """Creer un client en prenant l'IP et le port du serveur"""
    def __init__(self, ipServ, portServ):
        self.sock = socket()
        self.sock.connect((ipServ, portServ))

    """Demande au serveur une connection en lui passant un pseudo, retourne la reponse"""
    def connectionRequest(self,pseudo):
        request = {
            "pseudo": pseudo,
            "exchange": "login"
        }
        self.sendRequest(request)
        return self.waitAnswer()

    """Demande au serveur de se placer en lui passant un tuple contenant la colonne et la ligne, retourne la reponse"""
    def placementRequest(self, coord):
        request = {
            "exchange":"placement",
            "data":[coord[0],coord[1]]
        }
        self.sendRequest(request)
        return self.waitAnswer()

    """Demande au serveur de se deplacer en lui indiquant une direction, retourne la reponse"""
    def moveRequest(self, direction):
        request = {
            "exchange":"move",
            "data":direction
        }
        self.sendRequest(request)
        return self.waitAnswer()

    """Demande au serveur une copie de la map, retourne la reponse"""
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

    """Demande au serveur une liste des joueurs et de leurs ressources, retourne la reponse"""
    def refreshPlayer(self):
        request = {
            "exchange": "listof"
        }
        self.sendRequest(request)
        answer = self.waitAnswer()
        return answer["data"]

    """Demande au serveur de se deconnecter, retourne la reponse"""
    def logoutRequest(self):
        request = {
            "exchange": "logout"
        }
        self.sendRequest(request)
        answer = self.waitAnswer()
        self.sock.close()
        return answer

    """Demande au serveur de changer de pseudo en lui passant le nouveau pseudo, retourne la reponse"""
    def modRequest(self, newPseudo):
        request = {
            "exchange": "mod",
            "data":newPseudo
        }
        self.sendRequest(request)
        return self.waitAnswer()

    """Demande au serveur de se mettre en pause, retourne la reponse"""
    def pauseRequest(self):
        request = {
            "exchange": "pause"
        }
        self.sendRequest(request)
        return self.waitAnswer()

    """Demande au serveur d'enlever la pause, retourne la reponse"""
    def continueRequest(self):
        request = {
            "exchange": "continue"
        }
        self.sendRequest(request)
        return self.waitAnswer()
    
    """Prend un dictionnaire en paramètre le convertit en JSON et l'envoie au serveur"""
    def sendRequest(self, request):
        request = json.dumps(request)
        request = request.encode()
        self.sock.send(request)

    """Action bloquante, attend pour une reponse du serveur et retourne cette reponse"""
    def waitAnswer(self):
        answer = self.sock.recv(1024)
        answer = json.loads(answer)
        return answer