import socket
import threading
import datetime
import sys
import signal
if len(sys.argv) < 4:
    print("ERROR: Argumentos insuficientes.")
    sys.exit(1)
MAX_LARGO_MENSAJE = 255
puerto_propio = int(sys.argv[1]) 
ipAuth = sys.argv[2]
portAuth = int(sys.argv[3])

#Todas las interfaces de red
ip_propio = '0.0.0.0'


#Socket receptor para P2P
socket_servidorP2P = socket.socket(socket.AF_INET, socket.SOCKET_STREAM)
socket_servidorP2P.bind((ip_propio, puerto_propio))

#Socket emisor para P2P
socket_clienteP2P = socket.socket(socket.AF_INET, socket.SOCKET_STREAM)








def conexion_auth():
    #Socket emisor para Auth
    socket_clienteAuth = socket.socket(socket.AF_INET, socket.SOCKET_STREAM)
    
    try:
        socket_clienteAuth.connect((ipAuth, portAuth))
        print("Conectándose a servidor de autenticación..")

        #Recibir saludo
        saludo = socket_clienteAuth.recv(1024).decode('utf-8')
        print(f"> {saludo.strip()}")

        #Pedir datos del usuario
        usuario = input("Usuario: ")
        clave = input("Clave: ")

        #calcular MD5 y empaquetar
        clave_md5 = hashlib.md5(clave.encode('utf-8')).hexdigest()
        peticion = f"{usuario}-{clave-md5}\r\n"

        #Envia a Auth "peticion"
        socket_clienteAuth.sendall(peticion.encode('utf-8'))

        #Recibir respuesta (SI o NO)
        respuesta = socket_clienteAuth.recv(1024).decode('utf-8')

        if "SI" in respuesta:
            nombre_completo = socket_clienteAuth.recv(1024).decode('utf-8')
            print(f"Bienvenido {nombre_completo}")
            return True
        else:
            print("Acceso denegado (NO)")
            return False
    except Exception:
        print(f"Error en la comunicacion con Auth Server {Exception}")
        return False

    finally:
        #Se cierra socket
        socket_clienteAuth.close()


def hilo_emisor_p2p():
    #Despierto socket emisor
    socket_clienteP2P.connect((ipAuth, portAuth))
    print("Conectándose al peer..")


    threading.Thread(target=hilo_emisor_p2p args=(, ) daemon=True)


def hilo_receptor_p2p():
    #Despierto socket receptor
    socket_servidorP2P.listen()
    print("Escuchando..")
    socket_servidorP2P.accept()
    print("Aceptando conexiones entrantes..")

    threading.Thread(target=hilo_receptor_p2p args=(, ) daemon=True)







def enviar(socket_cliente, mensaje):
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