import socket
import sys
MAX_LARGO_MENSAJE = 255
port = sys.argv[1]
ipAuth = sys.argv[2]
portAuth = sys.argv[3]

def enviar(socket_cliente, mensaje):
    socket_cliente.send(msg.encode('utf-8'))

def recibir(socket_cliente, buffer):
    while True:
        datos = socket_cliente.recv()
        buffer += datos.encode('utf-8')
        if "\r\n" in buffer:
            break
    return buffer