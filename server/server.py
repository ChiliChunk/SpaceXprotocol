from socket import *
import sys
import time
import threading
import json
import os.path
import Robot
from random import randint

lockName = threading.Semaphore()
mapPseudo = {}
cellsWithRessources = {}


def addUser(pseudo, socket):
    lockName.acquire()
    mapPseudo[socket] = Robot.Robot(pseudo)
    lockName.release()
    return {"code": 200}


def removeUser(socket):
    lockName.acquire()
    del mapPseudo[socket]
    lockName.release()
    return {"code": 200}

def mapMessage(row,col):
    print(row,col)
    result = {}
    return result


def writeLogLine(fileName, pseudo, command, code):
    with open(fileName, "a") as f:
        f.write(f"{round(time.time())}   {pseudo}   {command}   {code}\n")


def traiter_client(socket_client, conf):
    connected = True
    while connected:
        wrapper = socket_client.makefile()
        ligne = wrapper.readline()[:-1]
        print('ENVOYE PAR CLIENT')
        print(ligne)
        jsonData = {}
        message = ''
        canProcess = False
        try:
            jsonData = json.loads(ligne)
            canProcess = True
        except Exception:
            message = {"code": 499}
        print(jsonData)
        if canProcess:
            if jsonData["exchange"] == 'login':
                message = addUser(jsonData["pseudo"], sock_client)
            if jsonData["exchange"] == "logout":
                connected = False
                message = removeUser(sock_client)
            if jsonData["exchange"] == "map":
                message = mapMessage(conf["map_number_row"] , conf["map_number_col"])

            writeLogLine(conf["logs"], mapPseudo[sock_client].name, jsonData["exchange"],
                         message["code"])  # FIXME pseudo undefined pour le logout
        else:
            if sock_client in mapPseudo.keys():
                writeLogLine(conf["logs"],
                             mapPseudo[sock_client].name if sock_client in mapPseudo.keys() else "unknown",
                             "BAD_FORMAT", message["code"])  # FIXME pseudo undefined pour le logout
        socket_client.send((json.dumps(message) + "\n").encode())


def loadConfiguration():
    configuration = {}
    conf = open('spaceXserver.conf', 'r')
    for ligne in conf:
        currentLine = ligne
        currentLine.replace("\n", "")
        data = currentLine.split("=")
        configuration[data[0]] = data[1].replace("\n", "")
    return configuration


def createMap(row, col, ressources):
    print(row, col)
    result = {}
    ressourcesDict = json.loads(ressources)
    for i in range(row):
        for j in range(col):
            currentRessources = []
            for key, value in ressourcesDict.items():
                if randint(1, 100) <= value:
                    currentRessources.append(key)
            if len(currentRessources) > 0:
                result[(i, j)] = currentRessources
    return result

if __name__ == '__main__':
    conf = loadConfiguration()
    cellsWithRessources = createMap(int(conf['map_number_row']), int(conf['map_number_col']), conf["ressources"])
    sock_server = socket()  # TCP socket
    sock_server.bind(("", int(conf['port'])))
    print(f"Server listening on port : {conf['port']}")
    sock_server.listen(int(conf['client_number']))
    while True:
        try:
            sock_client, adr_client = sock_server.accept()
            print(f"Connection de {adr_client}")
            threading.Thread(target=traiter_client, args=(sock_client,conf)).start()
        except KeyboardInterrupt:
            break
    sock_server.shutdown(SHUT_RDWR)
    print('\nshutting down')
    # for t in threading.enumerate():
    #     if t != threading.main_thread():
    #         t.join()
    sys.exit(0)
