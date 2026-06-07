import socket
import threading
from datetime import datetime
import sys
import signal
import hashlib
import os

#-Matías Acuña 5.639.240-5
#-Bruno Ferraro 5.418.881-4
#-Damián Páez 5.135.346-8

if len(sys.argv) < 4:
    print("ERROR: Argumentos insuficientes.")
    sys.exit(1)
MAX_LARGO_MENSAJE = 255
port = int(sys.argv[1])
ipAuth = sys.argv[2]
portAuth = int(sys.argv[3])
ips_conocidas = set()

def autenticar(ip_auth, port_auth, usuario):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip_auth, port_auth))
    leer_linea_crlf(sock)
    contrasenia = hashlib.md5(usuario.encode("utf-8")).hexdigest()
    msj = f"{usuario}-{contrasenia}\r\n"
    sock.sendall(msj.encode("utf-8"))
    res = leer_linea_crlf(sock)
    if res is None:
        sock.close()
        return None
    res = res.decode("utf-8").strip()
    if res == "NO":
        sock.close()
        return None
    if res == "SI":
        nombre = leer_linea_crlf(sock)
        if nombre is None:
            sock.close()
            return None
        nombre = nombre.decode("utf-8").strip()
        sock.close()
        return nombre
    sock.close()
    return None
    

def iniciar_receptor(port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("", port))
    server_sock.listen()
    return server_sock


def loop_receptor(server_sock):
    while True:
        conn, addr = server_sock.accept()
        th = threading.Thread(target=handle_incoming, args=(conn, addr))
        th.start()

def handle_incoming(conn, addr):
    msj = leer_linea_crlf(conn)
    if msj is None:
         conn.close()
         return
    fecha = datetime.now().strftime("[%Y.%m.%d %H:%M]")
    msj = msj.decode("utf-8").strip()
    if msj.startswith("MSG"):
        partes = msj.split(" ", 2)
        if len(partes) < 3:
            print("Mensaje invalido")
            conn.close()
            return
    else:
        partes = msj.split(" ", 3)
        if len(partes) < 4:
            print("Mensaje invalido")
            conn.close()
            return
    ips_conocidas.add(addr[0])
    if partes[0] == "MSG":
        print(f"{fecha} {addr[0]} {partes[1]} dice: {partes[2]}")
    elif partes[0] == "FILE":
        usuario = partes[1]
        nombre = partes[2]
        try:
            tamanio = int(partes[3])
        except ValueError:
             print("Tamaño de archivo invalido")
             conn.close()
             return
        contenido = leer_exactamente(conn, tamanio)
        if contenido is None:
            print(f"{fecha} {addr[0]} <Error Recibiendo Archivo de {usuario}>")
            conn.close()
            return 
        else:
            archivo = open(nombre, "wb")
            archivo.write(contenido)
            archivo.close()
        print(f"{fecha} {addr[0]} <Recibido ./{nombre} de {usuario}>")
    else:
        print ("Tipo de mensaje invalido")
    conn.close()


def loop_emisor(usuario, port_destino_default):
    while True:
        linea = input()
        resultado = parsear_entrada(linea)
        if resultado is None:
            continue
        tipo, destino, contenido = resultado
        if tipo == "MSG":
            destino_r = resolver_destino(destino)
            if destino_r is None:
                continue
            ips_conocidas.add(destino_r)
            enviar_mensaje(destino_r, port_destino_default, usuario, contenido)
        elif tipo == "FILE":
            destino_r = resolver_destino(destino)
            if destino_r is None:
                continue
            ips_conocidas.add(destino_r)
            enviar_archivo(destino_r, port_destino_default, usuario, contenido)
        elif tipo == "BROADCAST_MSG":
            ips = resolver_broadcast()
            for ip in ips:
                enviar_mensaje(ip, port_destino_default, usuario, contenido)
        elif tipo == "BROADCAST_FILE":
            ips = resolver_broadcast()
            for ip in ips:
                enviar_archivo(ip, port_destino_default, usuario, contenido)
        else:
            print("Tipo de entrada invalido")

def parsear_entrada(linea):
    linea = linea.strip()
    partes = linea.split(" ", 1)

    if len(partes) < 2:
        print("Entrada invalida")
        return None

    destino = partes[0]
    resto = partes[1].strip()

    if destino == "" or resto == "":
        print("Entrada invalida")
        return None

    if resto.startswith("&file "):
        path = resto[6:].strip()

        if path == "":
            print("Entrada invalida")
            return None

        if destino == "*":
            tipo = "BROADCAST_FILE"
        else:
            tipo = "FILE"

        contenido = path

    else:
        if destino == "*":
            tipo = "BROADCAST_MSG"
        else:
            tipo = "MSG"

        contenido = resto

    return tipo, destino, contenido

def resolver_destino(destino):
    try:
        ip = socket.gethostbyname(destino)
        return ip
    except socket.gaierror:
        print("No se pudo resolver destino")
        return None


def enviar_mensaje(ip_destino, port_destino, usuario, mensaje):
    msjby= mensaje.encode("utf-8")
    if len(msjby) > MAX_LARGO_MENSAJE:
        print("Tamaño de mensaje excedido")
        return None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_destino, port_destino))
        paquete = armar_header_msg(usuario, msjby)
        sock.sendall(paquete)
        sock.close()
    except OSError as e:
        print(f"Error enviando a {ip_destino}:{port_destino}: {e}")
        return None


def enviar_archivo(ip_destino, port_destino, usuario, path):
    if not os.path.exists(path):
        print ("El archivo no existe o la ruta es incorrecta")
        return None
    nombre = os.path.basename(path)
    tamanio = os.path.getsize(path)
    archivo = open(path, "rb")
    contenido = archivo.read()
    archivo.close()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_destino, port_destino))
        header = armar_header_file(usuario, nombre, tamanio)
        sock.sendall(header)
        sock.sendall(contenido)
        sock.close()
    except OSError as e:
        print(f"Error enviando archivo a {ip_destino}:{port_destino}: {e}")
        return None


def leer_linea_crlf(sock):
    buffer =b""
    while b"\r\n" not in buffer:
        chunk = sock.recv(1)
        if chunk == b"":
            return None    
        buffer = buffer + chunk
    return buffer 


def leer_exactamente(sock, cantidad):
    buffer = b""
    while len(buffer) < cantidad:
        chunk = sock.recv(cantidad - len(buffer))
        if chunk == b"":
            return None
        buffer = buffer + chunk
    return buffer
  

def armar_header_msg(usuario, mensaje_bytes):
    msj = mensaje_bytes.decode("utf-8")
    h = f"MSG {usuario} {msj}\r\n"
    return h.encode("utf-8")
   

def armar_header_file(usuario, nombre_archivo, tamanio):
    h = f"FILE {usuario} {nombre_archivo} {tamanio}\r\n"
    return h.encode("utf-8")


def resolver_broadcast():
    return list(ips_conocidas)


def handlerCierre(senial, frame):
    print(f"Señal recibida: {senial}")
    print("Terminando el programa...")

    sys.exit(0)
    
def main():
    print("\nSistema de mensajeria\n")
    usuario = input("Ingrese su usuario: ")
    nombre = autenticar(ipAuth, portAuth, usuario)
    if nombre is None:
        print("Error de autenticacion")
        sys.exit(1)
    print(f"Bienvenido {nombre}")
    server_sock = iniciar_receptor(port)
    th_receptor = threading.Thread(target=loop_receptor, args=(server_sock,), daemon=True)
    th_receptor.start()
    print(f"Receptor escuchando en puerto {port}")
    loop_emisor(usuario, port)
    
    
    

signal.signal(signal.SIGINT, handlerCierre)
signal.signal(signal.SIGTERM, handlerCierre)


if __name__ == "__main__":
    main()
