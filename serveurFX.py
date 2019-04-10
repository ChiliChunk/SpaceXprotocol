from socket import *
import sys
import threading
import json
from random import randint
from robot import Robot
global taille_tampon, users, robots, robi

taille_tampon= 1024

"""Liste des utilisteurs, avec comme clé leur socket et comme valeur leur pseudo"""
users = {}

"""Liste des coordonnées de tout les robots"""
robots = []

"""Liste des robots avec comme clé leur pseudo et comme valeur leur(s) ressource(s)"""
robi = {}

"""Fonction appelée par le client lors de sa connexion. Verifie si la liste des users est vide, si oui elle crée
un nouvel objet avec comme clé la socket du client et comme valeur le pseudo.
Si users n'est pas vide, login teste si le pseudo donné en paramètre est present dans les valeurs de users : si non, elle crée un nouvel user dans le dictionnaire users,
sinon elle renvoie le code d'erreur 401"""
def login(socket_client, nom):
    global users
    if len(users)==0:
        users[socket_client] = nom
        reponse = {"code": 200}
        return reponse
    else:
        if nom not in users.values():
            users[socket_client] = nom
            reponse = {"code": 200}
            return reponse
        else:
            reponse = {"code": 401}
            return reponse

"""Logout est appelée quand le client veut se deconnecter, elle supprime ses coordonnées de la liste des robots, supprime le client de users, de robi et de la map"""
def logout(socket_client, x, y):
    global users
    x=int(x)
    y=int(y)
    if (x, y) in map.keys():
        del map[(x, y)]
    del robi[users[socket_client]]
    del users[socket_client]
    for i in range(len(robots)):
        if robots[i] == (x, y):
            del robots[i]
    reponse = {"code": 200}
    return reponse

"""Renvoie le pseudo de tout les utilisateurs avec les ressources qu'ils ont trouvé"""
def getPlayers():
    global users

    rep =[]
    for key in robi:
        if(robi[key]) != {}:
            rep.append({"pseudo": key, "ressources":robi[key]})
        else:
            rep.append({"pseudo":key})
    reponse = {"data": rep}

    return reponse

"""Change le nom d'un utilisateur si le nom donné en paramètre n'est pas déja présent dans les valeurs de users, sinon 
renvoie un code 401"""
def changeName(socket_client, nom):
    global users
    if nom not in users.values():
        robi[nom] = robi[users[socket_client]]
        del robi[users[socket_client]]
        del users[socket_client]
        users[socket_client]=nom
        reponse = {"code": 200}
        return reponse
    else:
        reponse = {"code": 401}
        return reponse

"""Renvoie le nb max de colonnes et de lignes précisés dans le fichier conf, la liste robots avec les coordonnées de tout les robots présents, et self, qui représente 
les coordonnées du client"""
def refresh():
    reponse = {"code": 200,
               "data": {"dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                        "robots": robots, "self" : (int(rob.x), int(rob.y))}}
    return reponse


mutex = threading.Semaphore()

"""Fonction qui traite les requêtes du client, en fonction de si il est connecté ou pas"""
def traiter_client(socket_client, configuration): #CLIENT MESSAGE RECEIVED : [<pseudo>,<message>]
    global rob
    while True:
        connected = False
        while not connected:
            commande = socket_client.recv(1024).decode().upper()
            commande = json.loads(commande)
            com = commande['EXCHANGE']
            if com == "LOGIN":
                if login(socket_client, commande['PSEUDO']) == {"code": 200}:
                    connected=True
                    rob = Robot(commande['PSEUDO'])
                    reponse = {"code" : 200, "data": {"dimension" : (int(configuration['map_number_row']), int(configuration['map_number_col'])), "robots" : robots}}
                    socket_client.send((json.dumps(reponse) + "\n").encode())
                elif commande['PSEUDO'] in users.values():
                    reponse = {"code": 401}
                    socket_client.send((json.dumps(reponse) + "\n").encode())
        while connected:
            commande = socket_client.recv(1024).decode().upper()
            commande = json.loads(commande)
            com = commande['EXCHANGE']
            if com == "LOGOUT":
                logout(socket_client, rob.x, rob.y)
                connected = False
            elif com == "PLACEMENT":
                reponse = position(users[socket_client], commande['DATA'][0], commande['DATA'][1])
                socket_client.send((json.dumps(reponse) + "\n").encode())
            elif com == "LISTOF":
                reponse = getPlayers()
                socket_client.send((json.dumps(reponse) + "\n").encode())
            elif com == "REFRESH":
                reponse = refresh()
                socket_client.send((json.dumps(reponse) + "\n").encode())
            elif com == "MOVE":
                reponse = move(commande['DATA'])
                socket_client.send((json.dumps(reponse) + "\n").encode())
            elif com == "MOD":
                reponse = changeName(socket_client, commande['DATA'])
                socket_client.send((json.dumps(reponse) + "\n").encode())
            elif com == "PAUSE":
                pause = True
                reponse = {"code": 200}
                socket_client.send((json.dumps(reponse) + "\n").encode())
                while pause:
                    commande = socket_client.recv(1024).decode().upper()
                    commande = json.loads(commande)
                    com = commande['EXCHANGE']
                    if com == "CONTINUE":
                        reponse = {"code": 200}
                        socket_client.send((json.dumps(reponse) + "\n").encode())
                        pause = False
                    else:
                        reponse = {"code": 404}
                        socket_client.send((json.dumps(reponse) + "\n").encode())

            else :
                reponse = {"code": 404}
                socket_client.send((json.dumps(reponse) + "\n").encode())

"""Fonction créant la map en fonction du nombre de colonnes, de lignes, et de resources spécifiés dans le dossier de configuration. Les ressources 
 sont réparties aléatoirement"""
def create_map(lig, col, ressources):
    map = {}
    ress = json.loads(ressources)
    for i in range(lig):
        for j in range(col):
            currentRessources = []
            for key, val in ress.items():
                if randint(1, 100) <= val:
                    currentRessources.append(key)
            if len(currentRessources) > 0:
                map[(i, j)] = currentRessources
    return map

"""Fonction utilisée pour bouger le robot sur une des 8 cases qui lui sont adjacentes.
A chaque déplacement, il est vérifié que la position demandée n'est pas déjà occupée, qu'elle n'est pas en dehors de la grille, et si ce n'est pas le cas, 
la position du robot est supprimée de la liste, elle vérifie si la nouvelle case possède une ou des ressources, si oui elle les ajoute au robot du client. 
Pour finir elle modifie la position du robot en lui affectant la nouvelle."""
def move(position):
    position = int(position)
    reponse = ""
    if position==1:
        if (rob.x-1, rob.y-1) in robots:
            reponse = {"code": 403}
        elif (rob.x -1) < 0 or (rob.y - 1) < 0 or ((rob.x -1) < 0 and (rob.y - 1) < 0) :
            reponse = {"code" : 403}
        else :
            reponse = {"code": 200,
                       "data": {
                           "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                           "robots": robots, "self": (int(rob.x), int(rob.y))}}
            bla = map[(rob.x, rob.y)]
            del map[(rob.x, rob.y)]
            if (rob.x -1, rob.y-1) in map.keys():
                if map[(rob.x -1, rob.y-1)] == ['bois'] or map[(rob.x -1, rob.y-1)] == ['fer'] or map[(rob.x -1, rob.y-1)] == ['bois', 'fer']:
                    rob.addRessources(map[(rob.x -1, rob.y-1)])
                    robi[rob.name] = rob.ressources
            robots.remove((int(rob.x), int(rob.y)))
            rob.x -= 1
            rob.y -= 1
            map[(rob.x, rob.y)] = bla
            robots.append((rob.x, rob.y))
    elif position == 2:
        if (rob.x, rob.y-1) in robots:
            reponse = {"code": 403}
        elif(rob.y-1)<0:
            reponse = {"code": 403}
        else :
            reponse = {"code": 200,
                       "data": {
                           "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                           "robots": robots, "self": (int(rob.x), int(rob.y))}}
            bla = map[(rob.x, rob.y)]
            del map[(rob.x, rob.y)]
            if (rob.x, rob.y-1) in map.keys():
                if map[(rob.x, rob.y-1)] == ['bois'] or map[(rob.x, rob.y-1)] == ['fer'] or map[(rob.x, rob.y-1)] == ['bois', 'fer']:
                    rob.addRessources(map[(rob.x, rob.y-1)])
                    robi[rob.name] = rob.ressources
            robots.remove((int(rob.x), int(rob.y)))
            rob.y -= 1
            map[(rob.x, rob.y)] = bla
            robots.append((rob.x, rob.y))
    elif position==3:
        reponse = {"code": 200,
                   "data": {
                       "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                       "robots": robots, "self": (int(rob.x), int(rob.y))}}
        if (rob.x+1, rob.y-1) in robots:
            reponse = {"code": 403}
        elif (rob.x +1) > (int(reponse['data']['dimension'][0])-1) or (rob.y - 1) < 0 or ((rob.x +1) > (int(reponse['data']['dimension'][0])-1) and (rob.y - 1) < 0) :
            reponse = {"code" : 403}
        else :
            reponse = {"code": 200,
                       "data": {
                           "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                           "robots": robots, "self": (int(rob.x), int(rob.y))}}
            bla = map[(rob.x, rob.y)]
            del map[(rob.x, rob.y)]
            if (rob.x +1, rob.y-1) in map.keys():
                if map[(rob.x +1, rob.y-1)] == ['bois'] or map[(rob.x +1, rob.y-1)] == ['fer'] or map[(rob.x +1, rob.y-1)] == ['bois', 'fer']:
                    rob.addRessources(map[(rob.x +1, rob.y-1)])
                    robi[rob.name] = rob.ressources
            robots.remove((int(rob.x), int(rob.y)))
            rob.x += 1
            rob.y -= 1
            map[(rob.x, rob.y)] = bla
            robots.append((rob.x, rob.y))
    elif position == 4:
        if (rob.x-1, rob.y) in robots:
            reponse = {"code": 403}
        elif(rob.x-1)<0:
            reponse = {"code": 403}
        else :
            reponse = {"code": 200,
                       "data": {
                           "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                           "robots": robots, "self": (int(rob.x), int(rob.y))}}
            bla = map[(rob.x, rob.y)]
            del map[(rob.x, rob.y)]
            if (rob.x-1, rob.y) in map.keys():
                if map[(rob.x-1, rob.y)] == ['bois'] or map[(rob.x-1, rob.y)] == ['fer'] or map[(rob.x-1, rob.y)] == ['bois', 'fer']:
                    rob.addRessources(map[(rob.x-1, rob.y)])
                    robi[rob.name] = rob.ressources
            robots.remove((int(rob.x), int(rob.y)))
            rob.x -= 1
            map[(rob.x, rob.y)] = bla
            robots.append((rob.x, rob.y))
    elif position == 5:
        reponse = {"code": 200,
                   "data": {
                       "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                       "robots": robots, "self": (int(rob.x), int(rob.y))}}
        if (rob.x+1, rob.y) in robots:
            reponse = {"code": 403}
        elif (rob.x + 1) > (int(reponse['data']['dimension'][0]) - 1):
            reponse = {"code": 403}
        else:
            reponse = {"code": 200,
                       "data": {
                           "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                           "robots": robots, "self": (int(rob.x), int(rob.y))}}
            bla = map[(rob.x, rob.y)]
            del map[(rob.x, rob.y)]
            if (rob.x + 1, rob.y) in map.keys():
                if map[(rob.x +1, rob.y)] == ['bois'] or map[(rob.x + 1, rob.y)] == ['fer'] or map[(rob.x+1, rob.y)] == [
                    'bois', 'fer']:
                    rob.addRessources(map[(rob.x + 1, rob.y)])
                    robi[rob.name] = rob.ressources
            robots.remove((int(rob.x), int(rob.y)))
            rob.x += 1
            map[(rob.x, rob.y)] = bla
            robots.append((rob.x, rob.y))
    elif position == 6:
        reponse = {"code": 200,
                   "data": {
                       "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                       "robots": robots, "self": (int(rob.x), int(rob.y))}}
        if (rob.x-1, rob.y+1) in robots:
            reponse = {"code": 403}
        elif (rob.y + 1) > (int(reponse['data']['dimension'][0]) - 1) or (rob.x - 1) < 0 or (
                (rob.y + 1) > (int(reponse['data']['dimension'][0]) - 1) and (rob.x - 1) < 0):
            reponse = {"code": 403}
        else:
            reponse = {"code": 200,
                       "data": {
                           "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                           "robots": robots, "self": (int(rob.x), int(rob.y))}}
            bla = map[(rob.x, rob.y)]
            del map[(rob.x, rob.y)]
            if (rob.x - 1, rob.y + 1) in map.keys():
                if map[(rob.x - 1, rob.y + 1)] == ['bois'] or map[(rob.x - 1, rob.y + 1)] == ['fer'] or map[
                    (rob.x - 1, rob.y + 1)] == ['bois', 'fer']:
                    rob.addRessources(map[(rob.x - 1, rob.y + 1)])
                    robi[rob.name] = rob.ressources
            robots.remove((int(rob.x), int(rob.y)))
            rob.y += 1
            rob.x -= 1
            map[(rob.x, rob.y)] = bla
            robots.append((rob.x, rob.y))
    elif position == 7:
        reponse = {"code": 200,
                   "data": {
                       "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                       "robots": robots, "self": (int(rob.x), int(rob.y))}}
        if (rob.x, rob.y+1) in robots:
            reponse = {"code": 403}
        elif (rob.y + 1) > (int(reponse['data']['dimension'][0]) - 1):
            reponse = {"code": 403}
        else:
            reponse = {"code": 200,
                       "data": {
                           "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                           "robots": robots, "self": (int(rob.x), int(rob.y))}}
            bla = map[(rob.x, rob.y)]
            del map[(rob.x, rob.y)]
            if (rob.x, rob.y+1) in map.keys():
                if map[(rob.x, rob.y+1)] == ['bois'] or map[(rob.x, rob.y+1)] == ['fer'] or map[(rob.x, rob.y+1)] == ['bois', 'fer']:
                    rob.addRessources(map[(rob.x, rob.y+1)])
                    robi[rob.name] = rob.ressources
            robots.remove((int(rob.x), int(rob.y)))
            rob.y += 1
            map[(rob.x, rob.y)] = bla
            robots.append((rob.x, rob.y))
    elif position == 8:
        reponse = {"code": 200,
                   "data": {
                       "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                       "robots": robots, "self": (int(rob.x), int(rob.y))}}
        if (rob.x+1, rob.y+1) in robots:
            reponse = {"code": 403}
        elif (rob.x + 1) > (int(reponse['data']['dimension'][0]) - 1) or (rob.y + 1) > (int(reponse['data']['dimension'][0]) - 1) or (
                (rob.y + 1) > (int(reponse['data']['dimension'][0]) - 1) and (rob.x + 1) > (int(reponse['data']['dimension'][0]) - 1)):
            reponse = {"code": 403}
        else:
            reponse = {"code": 200,
                       "data": {
                           "dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                           "robots": robots, "self": (int(rob.x), int(rob.y))}}
            bla = map[(rob.x, rob.y)]
            del map[(rob.x, rob.y)]
            if (rob.x + 1, rob.y + 1) in map.keys():
                if map[(rob.x + 1, rob.y + 1)] == ['bois'] or map[(rob.x + 1, rob.y + 1)] == ['fer'] or map[
                    (rob.x + 1, rob.y + 1)] == ['bois', 'fer']:
                    rob.addRessources(map[(rob.x + 1, rob.y + 1)])
                    robi[rob.name] = rob.ressources
            robots.remove((int(rob.x), int(rob.y)))
            rob.y += 1
            rob.x += 1
            map[(rob.x, rob.y)] = bla
            robots.append((rob.x, rob.y))


    reponse = {"code": 200,
               "data": {"dimension": (int(configuration['map_number_row']), int(configuration['map_number_col'])),
                        "robots": robots, "self": [int(rob.x), int(rob.y)]}}
    return reponse



"""Verifie que la colonne donnée lors du premier positionnement est comprise entre 0 compris et le nombre max de colonnes
données"""
def checkcol(col):
    for key in map:
        bla = key
        if int(col) <= bla[0]:
            return True
    return False

"""Verifie que la ligne donnée lors du premier positionnement est comprise entre 0 compris et le nombre max de lignes
données"""
def checklig(lig):
    for key in map:
        bla = key
        if int(lig) <= bla[1]:
            return True
    return False

"""Fonction utilisée pour le premier placement du robot d'un client. Elle vérifie d'abord que le positionnement donné ne sort pas de la grille(404),
ensuite elle vérifie que la case n'est pas deja occupée du tout, si elle possède une ressource, et si elle n'est pas deja occupée par un autre robot (403)"""
def position(pseudo, lig, col):
    col, lig = int(col), int(lig)
    if checkcol(col) == True and checklig(lig) == True:
        if not (col, lig) in map.keys():
            map[(col, lig)] = pseudo
            rob.x, rob.y = col, lig
            reponse = {"code" : 200}
            robots.append((col, lig))
            robi[rob.name] = rob.ressources
            return reponse
        elif (col, lig) in map.keys() and (map[(col, lig)] == ['bois'] or map[(col, lig)] == ['fer']):
            rob.x, rob.y = col, lig
            rob.addRessources(map[(col, lig)])
            map[(col, lig)] = pseudo
            robots.append((col, lig))
            robi[rob.name] = rob.ressources
            reponse = {"code": 200}
            return reponse
        elif (col, lig) in map.keys() and (map[(col, lig)] == ['fer', 'bois'] or map[(col, lig)] == ['bois', 'fer']):
            rob.x, rob.y = col, lig
            rob.addRessources(map[(col, lig)])
            map[(col, lig)] = pseudo
            robots.append((col, lig))
            robi[rob.name] = rob.ressources
            reponse = {"code": 200}
            return reponse
        elif (col, lig) in map.keys() and map[(col, lig)] != (['bois'] or ['fer'] or ['bois', 'fer']):
            reponse = {"code": 403}
            return reponse
    else:
        reponse = {"code": 404}
        return reponse



if __name__ == '__main__':
    global map
    configuration = {}
    conf = open('spaceXserver.conf', 'r')
    for lig in conf:
        currentline= lig
        currentline.replace("\n", "")
        data = currentline.split("=")
        configuration[data[0]]=data[1].replace("\n", "")
    map = create_map(int(configuration['map_number_row']), int(configuration['map_number_col']), configuration["ressources"])
    print(map)
    sock_server = socket() #TCP socket
    sock_server.bind(("", int(configuration['port'])))
    print(f"Le serveur est en écoute sur le port : {int(configuration['port'])}")
    sock_server.listen(10)
    while True:
        try:
            sock_client, adr_client = sock_server.accept()
            print (f"Connexion de {adr_client}")
            threading.Thread(target=traiter_client, args=(sock_client, configuration)).start()
        except KeyboardInterrupt:
            break
    sock_server.shutdown(SHUT_RDWR)
    print('Fermeture du serveur\n')
