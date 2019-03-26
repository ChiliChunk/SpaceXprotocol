from socket import *
import sys
import threading


def sendNewConnection(pseudo):
    print(f"nouvelle connextion de {pseudo}")

def sendMessage(pseudo , message):
    print(f"message {message} de {pseudo}")


def traiter_client(socket_client): #CLIENT MESSAGE RECEIVED : [<pseudo>,<message>]
    wrapper = socket_client.makefile()
    package = wrapper.readline()


if len(sys.argv) != 2:
    print('Usage : python serverDNC.py <port>')
    sys.exit(1)

sock_server = socket() #TCP socket
sock_server.bind(("", int(sys.argv[1])))
print(f"Server listening on port : {sys.argv[1]}")
sock_server.listen(10)

while True:
    try:
        sock_client , adr_client = sock_server.accept()
        print (f"Connexion de {adr_client}")
        threading.Thread(target=traiter_client , args=(sock_client,)).start()
    except KeyboardInterrupt:
        break
sock_server.shutdown(SHUT_RDWR)
print('\nshutting down')
for t in threading.enumerate():
    if t != threading.main_thread():
        t.join()
sys.exit(0)