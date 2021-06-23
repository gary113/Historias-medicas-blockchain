import hashlib

import requests

BLOCKCHAIN_LOCALHOST = '127.0.0.1:80'


def hashear_bloque(bloque):
    return hashlib.sha256(str(bloque).encode('utf-8')).hexdigest()


def hashear_contrasenia(contrasenia):
    return hashlib.sha1(contrasenia.encode('utf-8')).hexdigest()


def obtener_cadena():
    r = requests.get('http://'+BLOCKCHAIN_LOCALHOST+'/cadena')
    return r.json()


def nueva_transaccion(datos):
    requests.post('http://'+BLOCKCHAIN_LOCALHOST +
                  '/agregar_transaccion', json=datos)
