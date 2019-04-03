from socket import *
import sys
import time
import threading
import json
import os.path

lockName = threading.Semaphore()
mapPseudo = {}


def addUser(pseudo, socket):
    lockName.acquire()
    mapPseudo[socket] = pseudo
    lockName.release()


def removeUser(socket):
    lockName.acquire()
    del mapPseudo[socket]
    lockName.release()

def writeLogLine(fileName , pseudo, command, code):
    with open(fileName, "a") as f:
        f.write(f"{round(time.time())} {pseudo} {command} {code} \n")

def traiter_client(socket_client, LogsFileName):
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
            print('in exectp')
            message = {"code" : 499}
        print(jsonData)
        if canProcess:
            if jsonData["exchange"] == 'login':
                addUser(jsonData["pseudo"], sock_client)
                message = {"code" : 200}
            if jsonData["exchange"] == "logout":
                connected = False
                removeUser(sock_client)
                message = {"code" : 200}
            writeLogLine(LogsFileName , mapPseudo[sock_client] , jsonData["exchange"] , message["code"]) #FIXME pseudo undefined pour le logout
        else :
            if sock_client in mapPseudo.keys():
                writeLogLine(LogsFileName ,  mapPseudo[sock_client] if sock_client in mapPseudo.keys() else "unknown", "BAD_FORMAT", message["code"]) #FIXME pseudo undefined pour le logout
        socket_client.send(json.dumps(message).encode())



def loadConfiguration():
    configuration = {}
    conf = open('spaceXserver.conf', 'r')
    for ligne in conf:
        currentLine = ligne
        currentLine.replace("\n", "")
        data = currentLine.split("=")
        configuration[data[0]] = data[1].replace("\n", "")
    return configuration

def createMap(row,col):
    print('create map')

if __name__ == '__main__':
    conf = loadConfiguration()
    createMap(conf['map_number_row'],conf['map_number_col'])
    print(conf)
    sock_server = socket()  # TCP socket
    sock_server.bind(("", int(conf['port'])))
    print(f"Server listening on port : {conf['port']}")
    sock_server.listen(int(conf['client_number']))
    while True:
        try:
            sock_client, adr_client = sock_server.accept()
            print(f"Connection de {adr_client}")
            threading.Thread(target=traiter_client, args=(sock_client,conf["logs"])).start()
        except KeyboardInterrupt:
            break
    sock_server.shutdown(SHUT_RDWR)
    print('\nshutting down')
    # for t in threading.enumerate():
    #     if t != threading.main_thread():
    #         t.join()
    sys.exit(0)
