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


def addUser(pseudo, socket):
    lockRobots.acquire()
    mapPseudo[socket] = Robot.Robot(pseudo)
    lockRobots.release()
    return {"code": 200}


def removeUser(socket):
    lockRobots.acquire()
    del mapPseudo[socket]
    lockRobots.release()
    return {"code": 200}


def mapMessage(row, col, socket):
    print(row, col)
    result = {}
    result["dimension"] = [col, row]
    robotList = []
    for sock, robot in mapPseudo.items():
        if sock != socket:
            robotList.append({"x": robot.x, "y": robot.y, "name": robot.name})
    result["robots"] = robotList
    selfRobot = mapPseudo[socket]
    result["self"] = {"x": selfRobot.x, "y": selfRobot.y, "name": selfRobot.name}
    result["code"] = 200
    print(result)
    return result


def setPaused(socket, isPaused):
    with lockRobots:
        mapPseudo[socket].isPaused = isPaused
        print(mapPseudo[socket])
        return {"code": 200}


def writeLogLine(fileName, pseudo, command, code):
    with open(fileName, "a") as f:
        f.write(f"{round(time.time())}   {pseudo}   {command}   {code}\n")


def changeName(socket, newName):
    with lockRobots:
        mapPseudo[socket].name = newName


def setPosition(socket, x, y, maxX, maxY):
    print(x)
    print(y)
    if x >= int(maxX) or x < 0 or y >= int(maxY) or y < 0:  # placement outside of the grid
        return {"code": 411}
    with lockRobots:
        for robot in mapPseudo.values():
            if robot.x == x and robot.y == y:  # try placement on another robot
                return {"code": 411}
        mapPseudo[socket].x = x
        mapPseudo[socket].y = y
        mapPseudo[socket].addRessources(getRessources(x, y))
        print(mapPseudo[socket])
        return {"code": 200}


def getRessources(x, y):
    with lockCells:
        if (x, y) in cellsWithRessources:
            temp = cellsWithRessources[(x, y)]
            del cellsWithRessources[(x, y)]
            return temp
        else:
            return []


def placement(socket, x, y, maxX, maxY):
    if mapPseudo[socket].x != None or mapPseudo[socket].y != None:
        return {"code": 405}
    return setPosition(socket, x, y, maxX, maxY)


def move(socket, index, maxX, maxY):
    if mapPseudo[socket].x == None or mapPseudo[socket].y == None:
        return {"code": 405}
    if index < 1 or index > 8:
        return {"code": 404}
    else:
        indexArray = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        return setPosition(socket, mapPseudo[socket].x + indexArray[index+1][0], mapPseudo[socket].y + indexArray[index+1][1],
                    maxX, maxY) #index +1 because placement start at 1


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

            print(message)
            writeLogLine(conf["logs"], mapPseudo[sock_client].name, jsonData["exchange"],
                         message["code"])  # FIXME pseudo undefined pour le logout
        else:
            if sock_client in mapPseudo.keys():
                writeLogLine(conf["logs"],
                             mapPseudo[sock_client].name if sock_client in mapPseudo.keys() else "unknown",
                             "BAD_FORMAT", message["code"])  # FIXME pseudo undefined pour le logout
                # TODO f'{socket_client.raddr[0]}:{socket_client.raddr[1] a la place de unknown
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
    print(getRessources(1, 1))
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
