import client


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
    if("self" in data):
        mine = data["self"]
    else:
        mine = [-1,-1]
    others = data["robots"]
    ret = ""
    for y in range(0, int(maxY)):
        for x in range(0, int(maxX)):

            if mine[0] == str(x) and mine[1] == str(y):
                ret += " O "
            elif [str(x), str(y)] in others:
                ret += " X "
            else:
                ret += " - "
        ret += "\n"
    return ret

def deplacement(client):
    print("Veuillez choisir une direction de déplacement pour le robot (en suivant le schéma ci-dessous ou R représente le robot)")
    print("1 2 3\n")
    print("4 R 5\n")
    print("6 7 8\n")
    choice = input()
    awnser =client.moveRequest(choice)
    return awnser["data"]

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

    c1 = client.Client(config["serverIp"], int(config["serverPort"]))

    while(True):
        pseudo = input("Entrez un pseudo entre 2 et 20 charactères \n")
        awnser = c1.connectionRequest(pseudo)
        print(awnser)
        if(awnser["code"]==200):
            grid = awnser["data"]
            print(grid)
            break
        else:
            print("Connection refusée par le serveur, code "+str(awnser["code"])+"\n")

    print(affichGrille(grid))
    #Besoin de rafraichir en cas d'erreur et d'afficher la signification du code
    while(True):
        print("Choissisez votre première position (entrez d'abord la colonne puis la ligne la numérotation commence à 0)\n")
        x = input("Entrez x: ")
        y = input("\nEntrez y: ")
        awnser = c1.placementRequest([x,y])
        if(awnser["code"] == 200):
            print("testest")
            grid = c1.refreshRequest()
            print(grid)
            break
        else:
            print("Placement refusé par le serveur, code "+str(awnser["code"])+"\n")
            exit(1)

    while(True):
        print(affichGrille(grid))
        print("\n Choissisez une action a effectuer : \n")
        choice = input(" 1) Se déplacer \n 2) Mettre en pause \n 3) Afficher la liste des joueurs  \n 4) Actualiser la grille \n 5) Changer de pseudo \n 6) Enlever la pause \n 7) Se déconnecter \n")
        choice =int(choice)
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
