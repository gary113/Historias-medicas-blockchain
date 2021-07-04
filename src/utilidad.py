import hashlib
import json
import socket

import requests

PUERTO_BLOCKCHAIN = '80'
LOCALHOST = '127.0.0.1'
RUTA = 'http://{}:{}{}'


def hashear_bloque(bloque):
    return hashlib.sha256(str(bloque).encode('utf-8')).hexdigest()


def hashear_contrasenia(contrasenia):
    return hashlib.sha1(contrasenia.encode('utf-8')).hexdigest()


def obtener_cadena_local():
    with open('bdJson.json', 'r') as f:
        return json.loads(f.read())


def obtener_cadena_remota(ip):
    r = requests.get(RUTA.format(ip, PUERTO_BLOCKCHAIN, '/cadena'))
    return r.json()


def nueva_transaccion(datos):
    requests.post(RUTA.format(LOCALHOST, PUERTO_BLOCKCHAIN,
                              '/agregar_transaccion'), json=datos)


def hacer_ping(ip):
    try:
        requests.get(RUTA.format(ip, PUERTO_BLOCKCHAIN,
                                 '/verificar_conexion'), timeout=0.01)
        return True
    except:
        return False


def conseguir_ip_local():

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))

        return sock.getsockname()[0]

    except socket.error:

        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            return '127.0.0.1'

    finally:
        sock.close()
