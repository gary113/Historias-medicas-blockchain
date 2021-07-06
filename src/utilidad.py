import hashlib
import json
import socket

import requests

PUERTO_BLOCKCHAIN = '80'
LOCALHOST = '127.0.0.1'
RUTA = 'http://{}:{}{}'
MENSAJE_TRANSACCION = 'Transacción registrada correctamente'


def hashear(datos):
    transaccion = json.dumps(datos).encode('utf-8')
    return hashlib.sha256(transaccion).hexdigest()


def hashear_contrasenia(contrasenia):
    return hashlib.sha1(contrasenia.encode('utf-8')).hexdigest()


def obtener_cadena_local():
    with open('bdJson.json', 'r') as f:
        return json.loads(f.read())


def obtener_cadena_remota(ip):
    r = requests.get(RUTA.format(ip, PUERTO_BLOCKCHAIN, '/cadena'))
    return r.json()


def obtener_transacciones_remotas(ip):
    transacciones = requests.get(RUTA.format(
        ip, PUERTO_BLOCKCHAIN, '/transacciones'))
    info_transacciones = requests.get(RUTA.format(
        ip, PUERTO_BLOCKCHAIN, '/info_transacciones'))

    return transacciones.json(), info_transacciones.json()


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


def buscar_bloques_corruptos(cadena):

    lista_revision = []
    previous_block = cadena[0]
    block_index = 1

    while block_index < len(cadena):

        bloque = cadena[block_index]
        previous_proof = previous_block['proof']
        proof = bloque['proof']
        hash_operation = hashlib.sha256(
            str(previous_proof**2+proof).encode()).hexdigest()

        if bloque['previous_hash'] != hashear(previous_block['transactions']) or not hash_operation.startswith('0'*3) or bloque['current_hash'] != hashear(bloque['transactions']):
            lista_revision.append(0)
        else:
            lista_revision.append(1)

        previous_block = bloque
        block_index += 1

    return lista_revision
