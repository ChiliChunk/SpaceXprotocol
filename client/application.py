import client
import os
from colorama import Fore, Back, Style

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

            if str(mine[0]) == str(x) and str(mine[1]) == str(y):
                ret += " O  "
            elif [x, y] in others:
                ret += " X  "
            else:
                ret += " -  "
        ret += "\n\n"
    print(ret)
    print("\n Les X symbolisent les autres robot, le O représente votre robot")


def deplacement(client):
    print("Veuillez choisir une direction de déplacement pour le robot (en suivant le schéma ci-dessous ou R représente le robot)")
    print("1  2  3\n\n")
    print("4  R  5\n\n")
    print("6  7  8\n\n")
    choice = input()
    anwser =client.moveRequest(choice)
    if (anwser["code"] != 200):
        os.system("clear")
        print("DEPLACEMENT IMPOSSIBLE !\n")
        input("Appuyer sur n'importe quelle touche pour continuer")
    else:
        if("ressource" in anwser["data"]):
            os.system("clear")
            print("Vous avez trouvé : \n")
            for res in anwser["data"]["ressource"]:
                print(res+"\n")
            print("\n")
            input("Appuyer sur n'importe quelle touche pour continuer")

def afficherJoueurs(client):
    os.system("clear")
    anwser = client.refreshPlayer()
    print("Tous les joueurs :")
    for play in anwser:
        print("\t"+play["pseudo"])
        if "ressources" in play:
            for res in play["ressources"]:
                print("\t\t"+res+ " : "+ str(play["ressources"][res])+"\n")
        print("\n")
    input("Appuyer sur n'importe quelle touche pour continuer")

def mettreEnPause(client):
    client.pauseRequest()
    os.system("clear")
    print("\t *** EN PAUSE *** \n")
    input("Appuyer sur n'importe quelle touche pour redémarrer le programme")
    client.continueRequest()


def changerPseudo(client):
    choice = input("Entrez un nouveau pseudo\n")
    client.modRequest(choice)

if __name__ == "__main__":
    config = loadConfiguration()

    c1 = client.Client(config["serverIp"], int(config["serverPort"]))
    while(True):
        pseudo = input("Entrez un pseudo entre 2 et 20 charactères \n")
        anwser = c1.connectionRequest(pseudo)
        if(anwser["code"]==200):
            grid = anwser["data"]
            break
        else:
            print("Connection refusée par le serveur, code "+str(anwser["code"])+"\n")

    affichGrille(grid)
    #Besoin de rafraichir en cas d'erreur et d'afficher la signification du code
    while(True):
        print("Choisissez votre première position \n")
        x = input("Entrez la colonne (entre 0 et "+str(grid["dimension"][0]) + " non-inclus) :")
        y = input("\nEntrez la ligne (entre 0 et "+str(grid["dimension"][1]) + " non-inclus) :")
        try :
            if(int(x) > 0 and int(x)< int(grid["dimension"][0]) and int(y)>0 and int(y)and int(grid["dimension"][1])):
                anwser = c1.placementRequest([x, y])
                if (anwser["code"] == 200):
                    grid = c1.refreshRequest()
                    break
                else:
                    print("Placement refusé par le serveur, code " + str(anwser["code"]) + "\n")
        except ValueError :
           pass
        print("Veuillez entrez un entier !")


    while(True):
        os.system("clear")
        print("~~~~~~~~~~~~SPACE X~~~~~~~~~~~~\n")
        affichGrille(grid)

        print("\n Choissisez une action a effectuer : \n")
        choice = input(" 1) Se déplacer \n 2) Mettre en pause \n 3) Afficher la liste des joueurs \n 4) Changer de pseudo \n 5) Se déconnecter \n")
        choice =int(choice)
        if(choice==1):
            deplacement(c1)
            grid = c1.refreshRequest()
        elif(choice==2):
            mettreEnPause(c1)
        elif(choice ==3):
            afficherJoueurs(c1)
            grid = c1.refreshRequest()
        elif(choice ==4):
            changerPseudo(c1)
            grid = c1.refreshRequest()
        elif(choice==5):
            c1.logoutRequest()
            print("Deconnexion réussie")
            exit(0)
        else:
            print("Choix invalide merci de réessayer \n")

    c1.sock.close()
