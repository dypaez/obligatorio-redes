import socket
import threading
from datetime import datetime
import sys
import signal
import hashlib
import os
if len(sys.argv) < 4:
    print("ERROR: Argumentos insuficientes.")
    sys.exit(1)
MAX_LARGO_MENSAJE = 255
port = int(sys.argv[1])
ipAuth = sys.argv[2]
portAuth = int(sys.argv[3])

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
    
#crear socket cliente, 
#conectarse a ipAuth:portAuth
#leer banner inicial del auth
#calcular md5(clave)
#mandar usuario-md5(clave)
#leer respuesta
#si SI, leer/devolver nombre completo
#si NO, devolver None
#cerrar socket

#receptor

def iniciar_receptor(port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("", port))
    server_sock.listen()
    return server_sock
#crear socket TCP
#setsockopt reuseaddr
#bind(("0.0.0.0" o "", port_local) o bind(("127.0.0.1", port_local)) según prueba
#listen()
#devolver server_socket

def loop_receptor(server_sock):
    while True:
        conn, addr = server_sock.accept()
        th = threading.Thread(target=handle_incoming, args=(conn, addr))
        th.start()
#while programa_activo:
#conn, addr = server_socket.accept()
#crear thread para handle_incoming(conn, addr)

def handle_incoming(conn, addr):
    msj = leer_linea_crlf(conn)
    if msj is None:
         conn.close()
         return
    msj = msj.decode("utf-8").strip()
    fecha = datetime.now().strftime("[%Y.%m.%d %H:%M]")
    print(f"{fecha} {addr[0]} {msj}")
    conn.close()
#leer lo que llega por conn
#decidir si es mensaje o archivo
#si es mensaje: imprimir fecha, ip, usuario, dice, mensaje
#si es archivo: guardar archivo en directorio actual
#si hay error de archivo: imprimir error
#cerrar conn

#emisor

def loop_emisor(usuario, port_destino_default):
    while True:
        linea = input()
        resultado = parsear_entrada(linea)
        if resultado is None:
            continue
        destino, mensaje = resultado
        enviar_mensaje(destino, port_destino_default, usuario, mensaje)
#leer líneas de stdin
#llamar parsear_entrada(linea)
#según el tipo, llamar enviar_mensaje o enviar_archivo
#si es broadcast, resolver destinos y mandar a varios

def parsear_entrada(linea):
    linea = linea.strip()
    partes = linea.split(" ", 1)
    if len(partes) < 2:
        print("Entrada invalida")
        return None
    if partes[1] == "":
        print("Entrada invalida")
        return None
    destino = partes[0]
    if destino == "":
        print("Entrada invalida")
        return None
    mensaje = partes[1]
    return destino, mensaje
#distinguir estos casos:

#192.168.33.15 Feliz Cumple!!!!!
#tecnoinf315.esi.edu.uy Feliz Cumple!!!!!
#tecnoinf315 Feliz Cumple!!!!!

#* Gracias a todos

#192.168.33.15 &file ./foto.jpg
#tecnoinf315 &file ./foto.jpg
#* &file ./foto.jpg

#salida conceptual
#tipo: MSG_DIRECTO / MSG_BROADCAST / FILE_DIRECTO / FILE_BROADCAST
#destino: ip/host/*
#contenido: mensaje o path

def resolver_destino(destino):
    pass
#si destino es IP, usarlo
#si destino es hostname, resolverlo

def enviar_mensaje(ip_destino, port_destino, usuario, mensaje):
    msjby= mensaje.encode("utf-8")
    if len(msjby) > MAX_LARGO_MENSAJE:
        print("Tamaño de mensaje excedido")
        return None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_destino, port_destino))
    paquete = mensaje + "\r\n"
    sock.sendall(paquete.encode("utf-8"))
    sock.close()

#validar largo <= 255
#crear socket cliente
#connect(ip_destino, port_destino)
#armar paquete de mensaje
#sendall(paquete)
#close

def enviar_archivo(ip_destino, port_destino, usuario, path):
    pass
#verificar que el archivo exista
#obtener nombre del archivo
#obtener tamaño
#abrir archivo en modo binario
#crear socket cliente
#connect
#mandar header de archivo
#mandar bytes del archivo
#close

def leer_linea_crlf(sock):
    buffer =b""
    while b"\r\n" not in buffer:
        chunk = sock.recv(1024)
        if chunk == b"":
            return None
            
        buffer = buffer + chunk
    return buffer 
#recibir bytes hasta encontrar b"\r\n"
#devolver la línea sin perder datos

def leer_exactamente(sock, cantidad):
    pass
#seguir haciendo recv hasta juntar exactamente cantidad bytes
#si recv devuelve b"", significa conexión cerrada antes de tiempo   

def armar_header_msg(usuario, mensaje_bytes):
    pass
#crear b"MSG usuario largo\r\n"    

def armar_header_file(usuario, nombre_archivo, tamaño):
    pass
#crear b"FILE usuario nombre_archivo tamaño\r\n"

def resolver_broadcast():
    pass
#consigue todas las ips con las que se hizo coneccion

def handlerCierre(senial, frame):
    print(f"Señal recibida: {senial}")
    print("Terminando el programa...")
#marcar programa como inactivo
#cerrar sockets abiertos si los tenés guardados
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
    th_receptor = threading.Thread(target=loop_receptor, args=(server_sock,))
    th_receptor.start()
    print(f"Receptor escuchando en puerto {port}")
    loop_emisor(usuario, port)
    
    
    

signal.signal(signal.SIGINT, handlerCierre)
signal.signal(signal.SIGTERM, handlerCierre)

# Estado actual:

# - autenticacion contra redes-auth funcionando
# - receptor TCP levanta bien en el puerto pasado por parametro
# - receptor queda corriendo en thread
# - acepta conexiones y muestra mensajes terminados en CRLF
# - emisor minimo funciona para mandar mensaje directo
# - parseo basico: destino + mensaje

# Falta:

# - armar protocolo real MSG con usuario y largo
# - que el receptor imprima: ip usuario dice: mensaje
# - resolver hostnames con socket.gethostbyname
# - soportar ip:puerto solo para pruebas locales, si hace falta
# - implementar FILE directo
# - implementar leer_exactamente para archivos
# - implementar headers FILE usuario nombre tamanio
# - broadcast liviano usando ips conocidas de la sesion
# - broadcast de archivos
# - manejar errores de conexion sin que explote todo
# - cierre limpio: cerrar server_sock y cortar threads si se puede
# - limpiar comentarios viejos cuando ya este funcionando


if __name__ == "__main__":
    main()
