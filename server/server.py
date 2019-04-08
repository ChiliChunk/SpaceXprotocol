from socket import *
import sys
import time
import threading
import json
import os.path
import Robot
from random import randint

lockRobots = threading.Semaphore()
lockCells = threading.Semaphore()
mapPseudo = {}
cellsWithRessources = {}

def checkLoggedIn(socket):
    return socket in mapPseudo

def addUser(pseudo, socket , col , row):
    if len(pseudo) < 2:
        return {"code" : 402}
    with lockRobots:
        for sock , robots in mapPseudo.items():
            if robots.name == pseudo:
                return {"code" : 401}
        mapPseudo[socket] = Robot.Robot(pseudo)
        return mapMessage(row,col,socket)


def removeUser(socket):
    with lockRobots:
        if not checkLoggedIn(socket):
            return {"code": 500}
        del mapPseudo[socket]
        return {"code": 200}


def mapMessage( col,row, socket):
    if not checkLoggedIn(socket):
        return {"code" : 500}
    else:
        result = {"data" : {}}
        result["data"]["dimension"] = [col, row]
        robotList = []
        for sock, robot in mapPseudo.items():
            if sock != socket:
                robotList.append(( str(robot.x) , str(robot.y)))
        result["data"]["robots"] = robotList
        selfRobot = mapPseudo[socket]
        if selfRobot.x != None:
            result["data"]["self"] = [str(selfRobot.x), str(selfRobot.y)]
        result["code"] = 200
        return result


def setPaused(socket, isPaused):
    with lockRobots:
        if not checkLoggedIn(socket):
            return {"code": 500}
        mapPseudo[socket].isPaused = isPaused
        return {"code": 200}


def writeLogLine(fileName, pseudo, command, code):
    with open(fileName, "a") as f:
        f.write(f"{round(time.time())}   {pseudo}   {command}   {code}\n")


def changeName(socket, newName):
    with lockRobots:
        if not checkLoggedIn(socket):
            return {"code": 500}
        mapPseudo[socket].name = newName


def setPosition(socket, x, y, maxX, maxY):
    if int(x) >= int(maxX) or int(x) < 0 or int(y) >= int(maxY) or int(y) < 0:  # placement outside of the grid
        print("ICI")
        return {"code": 411}
    with lockRobots:
        if mapPseudo[socket].isPaused:
            return {"code" : 410}
        for robot in mapPseudo.values():
            if robot.x == x and robot.y == y:  # try placement on another robot
                print("LA")
                return {"code": 411}
        mapPseudo[socket].x = x
        mapPseudo[socket].y = y
        mapPseudo[socket].addRessources(getRessources(x, y))
        print(mapPseudo[socket])
        return mapMessage(maxX,maxY,socket)


def getRessources(x, y):
    with lockCells:
        if (x, y) in cellsWithRessources:
            temp = cellsWithRessources[(x, y)]
            del cellsWithRessources[(x, y)]
            print()
            return temp
        else:
            return []


def placement(socket, x, y, maxX, maxY):
    if mapPseudo[socket].x != None or mapPseudo[socket].y != None:
        return {"code": 405}
    with lockRobots:
        if not checkLoggedIn(socket):
            return {"code": 500}
    return setPosition(socket, x, y, maxX, maxY)

def listOf(socket):
    with lockRobots:
        if not checkLoggedIn(socket):
            return {"code": 500}
        robots = []
        for sock , robot in mapPseudo.items():
            robots.append({"pseudo" : robot.name , "ressources" : robot.ressources})
        return ({"code" : 200 , "data" : robots})


def move(socket, index, maxX, maxY):
    if mapPseudo[socket].x == None or mapPseudo[socket].y == None:
        return {"code": 405}
    if int(index) < 1 or int(index) > 8:
        return {"code": 404}
    with lockRobots:
        if not checkLoggedIn(socket):
            return {"code": 500}
    indexArray = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    return setPosition(socket, int(mapPseudo[socket].x) + int(indexArray[int(index)-1][0]), int(mapPseudo[socket].y)+int(indexArray[int(index)-1][1]),maxX, maxY) #index -1 because placement start at 1


def traiter_client(socket_client, conf):
    connected = True
    while connected:
        # wrapper = socket_client.makefile()
        # ligne = wrapper.readline()
        ligne = socket_client.recv(1024)
        ligne = ligne.decode()
        print('ENVOYE PAR CLIENT')
        print(ligne)
        jsonData = {}
        message = {"code" : 491} #message for valid json but "exchange" not present in json
        canProcess = False
        try:
            jsonData = json.loads(ligne)
            canProcess = "exchange" in jsonData
        except Exception:
            message = {"code": 499}
        print(jsonData)
        print(canProcess)
        if canProcess:
            if jsonData["exchange"] == 'login':
                print('adduser')
                message = addUser(jsonData["pseudo"], sock_client , conf["map_number_col"], conf["map_number_row"])
            if jsonData["exchange"] == "logout":
                connected = False
                message = removeUser(sock_client)
            if jsonData["exchange"] == "map" or jsonData["exchange"] == "refresh":
                message = mapMessage(conf["map_number_row"], conf["map_number_col"], sock_client)
            if jsonData["exchange"] == "pause" or jsonData["exchange"] == "continue":
                message = setPaused(sock_client, jsonData["exchange"] == "pause")
            if jsonData["exchange"] == "changeName":
                message = changeName(socket_client, jsonData["pseudo"])
            if jsonData["exchange"] == "placement":
                message = placement(socket_client, jsonData["data"][0], jsonData["data"][1], conf["map_number_col"],
                                    conf["map_number_col"])
            if jsonData["exchange"] == "move":
                message = move(socket_client, jsonData["data"], conf["map_number_col"], conf["map_number_col"])
            if jsonData["exchange"] == "listof":
                message = listOf(socket_client)

            print(message)
            writeLogLine(conf["logs"], mapPseudo[sock_client].name if socket_client in mapPseudo else socket_client.getpeername()[0], jsonData["exchange"],
                     message["code"])
        else:
            writeLogLine(conf["logs"],
                         mapPseudo[sock_client].name if sock_client in mapPseudo else socket_client.getpeername()[0],
                         "BAD_FORMAT", message["code"])
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
    print(cellsWithRessources)
    sock_server = socket()  # TCP socket
    sock_server.bind(("", int(conf['port'])))
    print(f"Server listening on port : {conf['port']}")
    sock_server.listen(int(conf['client_number']))
    while True:
        try:
            sock_client, adr_client = sock_server.accept()
            print(f"Connection de {adr_client}")
            threading.Thread(target=traiter_client, args=(sock_client, conf)).start()
        except KeyboardInterrupt:
            break
    sock_server.shutdown(SHUT_RDWR)
    print('\nshutting down')
    # for t in threading.enumerate():
    #     if t != threading.main_thread():
    #         t.join()
    sys.exit(0)
