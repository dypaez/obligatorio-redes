import socket
import threading
from datetime import datetime
import sys
import signal
if len(sys.argv) < 4:
    print("ERROR: Argumentos insuficientes.")
    sys.exit(1)
MAX_LARGO_MENSAJE = 255
port = sys.argv[1]
ipAuth = sys.argv[2]
portAuth = sys.argv[3]


//autenticacion con ecriptamiento
//socket bind listen TCP
//threading
//manejar mensajes de usuario en terminal segun
//mensaje a otro, mensaje a todos*, file transfer a otro, filetransfer a todos*
//file transfer

def enviar(socket_cliente, mensaje):
    //connect?
    socket_cliente.send(mensaje.encode('utf-8'))

def recibir(socket_cliente, buffer):
    while True:
        datos = socket_cliente.recv()
        buffer += datos.encode('utf-8')
        if "\r\n" in buffer:
            break
    return buffer

def cerrar(senial, frame):
    print("Señal recibida: {senial}")
    print("Terminando el programa...")
    sys.exit(0)

signal.signal(signal.SIGINT, cerrar)
signal.signal(signal.SIGTERM, cerrar)
