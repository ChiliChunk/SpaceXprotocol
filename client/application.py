from SpaceXprotocol.client import client
def loadConfiguration():
    configuration = {}
    conf = open('spaceX.conf', 'r')
    for ligne in conf:
        currentLine = ligne
        currentLine.replace("\n", "")
        data = currentLine.split("=")
        configuration[data[0]] = data[1].replace("\n", "")
    return configuration


def affichGrille(data):
    maxX = data["dimension"][0]
    maxY = data["dimension"][1]
    mine = data["self"]
    others = data["robots"]
    ret = ""
    for x in range(0, maxX):
        for y in range(0, maxY):
            if mine[0] == x and mine[1] == y:
                ret += " O "
            elif [x, y] in others:
                ret += " X "
            else:
                ret += " _ "
        ret += "\n"
    return ret

def deplacement(client):
    print("Veuillez choisir une direction de déplacement pour le robot (en suivant le schéma ci-dessous ou R représente le robot)")
    print("1 2 3\n")
    print("4 R 5\n")
    print("6 7 8\n")
    choice = input()
    awnser =client.moveRequest(choice)
    return awnser["data"]["map"]

def afficherJoueurs(client):
    awnser = client.refreshPlayer()
    print("Tous les joueurs :")
    for play in awnser["data"]:
        print(play["pseudo"]+ "\n")

def changerPseudo(client):
    choice = input("Entrez un nouveau pseudo")
    client.modRequest(choice)
if __name__ == "__main__":
    config = loadConfiguration()

    c1 = client.Client(config["serverIP"], config["serverPort"])

    while(True):
        pseudo = input("Entrez un pseudo entre 2 et 20 charactères \n")
        awnser = c1.connectionRequest(pseudo)
        if(awnser["code"]==200):
            grid = awnser["data"]["map"]
            break
        else:
            print("Connection refusée par le serveur, code "+awnser["code"]+"\n")

    print(affichGrille(grid))
    #Besoin de rafraichir en cas d'erreur et d'afficher la signification du code
    while(True):
        x = input("Choissisez votre première position (entrez d'abord la colonne puis la ligne la numérotation commence à 0)")
        y = input()
        awnser = c1.placementRequest([x,y])
        if(awnser["code"] == 200):
            grid = awnser["data"]["map"]
            break
        else:
            print("Placement refusé par le serveur, code "+awnser["code"]+"\n")

    while(True):
        print(affichGrille(grid))
        print("\n Choissisez une action a effectuer : \n")
        choice = input("1) Se déplacer \n 2) Mettre en pause \n 3)Afficher la liste des joueurs  \n 4) Actualiser la grille \n 5) Changer de pseudo \n 6) Enlever la pause \n Se déconnecter")
        if(choice==1):
            grid = deplacement(c1)
        elif(choice==2):
            c1.pauseRequest()
        elif(choice ==3):
            afficherJoueurs(c1)
        elif(choice==4):
            grid = c1.refreshRequest()
        elif(choice ==5):
            changerPseudo(c1)
        elif(choice==6):
            c1.continueRequest()
        elif(choice ==7):
            c1.logoutRequest()
        else:
            print("Choix invalide merci de réessayer \n")

    c1.sock.close()
