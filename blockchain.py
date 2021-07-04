import datetime
import hashlib
import json
import logging

import requests
from flask import Flask, flash, render_template, request

from src.utilidad import (PUERTO_BLOCKCHAIN, RUTA, conseguir_ip_local,
                          hacer_ping, hashear_bloque, obtener_cadena_local,
                          obtener_cadena_remota)


class Blockchain:

    def __init__(self):

        self.dificultad_prueba = 3
        self.ip_local = conseguir_ip_local()
        self.peers = self.escanear_nodos()
        self.transacciones = []
        self.chain = []

        # Leer cadena local
        try:

            self.chain = obtener_cadena_local()

        # Si no existe cadena local
        except:

            block = {'index': len(self.chain) + 1,
                     'transactions': {
                'tipo': 0,
                'super': 1,
                'nombres': 'Gary',
                'apellidos': 'Candia Nina',
                'usuario': 'gcandia',
                'contrasenia': '7110eda4d09e062aa5e4a390b0a572ac0d2c0220'  # 1234
            },
                'timestamp': str(datetime.datetime.now()),
                'proof': 1,
                'previous_hash': 0}

            self.chain.append(block)

        finally:

            for ip in self.peers:
                if ip != self.ip_local:
                    cadena_remota = obtener_cadena_remota(ip)

                    if self.validar_cadena(cadena_remota):
                        self.chain = cadena_remota
                        break

            with open('bdJson.json', 'w') as file:
                json.dump(self.chain, file, indent=2)

            self.repartir_nodos()

    def crear_bloque_administrador(self, proof, previous_hash, datos):

        bloque = {'index': len(self.chain) + 1,
                  'transactions': {
            'tipo': 0,
            'super': datos['super'],
            'nombres': datos['nombres'],
            'apellidos': datos['apellidos'],
            'usuario': datos['usuario'],
            'contrasenia': datos['contrasenia']
        },
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }

        self.chain.append(bloque)
        return bloque

    def crear_bloque_paciente(self, proof, previous_hash, datos):

        bloque = {'index': len(self.chain) + 1,
                  'transactions': {
            'tipo': 1,
            'nombres': datos['nombres'],
            'apellidos': datos['apellidos'],
            'dni': datos['dni'],
            'nacimiento': datos['nacimiento'],
            'telefono': datos['telefono']
        },
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }

        self.chain.append(bloque)
        return bloque

    def crear_bloque_doctor(self, proof, previous_hash, datos):

        bloque = {'index': len(self.chain) + 1,
                  'transactions': {
            'tipo': 2,
            'nombres': datos['nombres'],
            'apellidos': datos['apellidos'],
            'dni': datos['dni'],
            'especialidad': datos['especialidad'],
            'telefono': datos['telefono'],
            'usuario': datos['usuario'],
            'contrasenia': datos['contrasenia']
        },
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }

        self.chain.append(bloque)
        return bloque

    def crear_bloque_registro_historia(self, proof, previous_hash, datos):

        bloque = {'index': len(self.chain) + 1,
                  'transactions': {
            'tipo': 3,
            'hash_paciente': datos['hash_paciente'],
            'hash_doctor': datos['hash_doctor'],
            'titulo': datos['titulo'],
            'descripcion': datos['descripcion'],
            'lugar': datos['lugar']
        },
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }

        self.chain.append(bloque)
        return bloque

    # 0=administrador 1=paciente, 2=doctor , 3=registro_historia
    def minar_bloque(self, tipo_bloque, datos):

        previous_block = self.chain[-1]
        previous_proof = previous_block['proof']
        proof = self.proof_of_work(previous_proof)
        previous_hash = self.hash(previous_block)

        print('Minando bloque tipo ', tipo_bloque, '...')

        if tipo_bloque == 0:

            bloque = self.crear_bloque_administrador(
                proof, previous_hash, datos)

        elif tipo_bloque == 1:

            bloque = self.crear_bloque_paciente(
                proof, previous_hash, datos)

        elif tipo_bloque == 2:

            bloque = self.crear_bloque_doctor(
                proof, previous_hash, datos)

        elif tipo_bloque == 3:

            bloque = self.crear_bloque_registro_historia(
                proof, previous_hash, datos)

        with open('bdJson.json', 'r+') as file:

            bd_json = json.load(file)
            bd_json.append(bloque)
            file.seek(0)

            json.dump(bd_json, file, indent=2)

        print('Bloque minado correctamente.')

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:

            hash_operation = hashlib.sha256(
                str(previous_proof**2+new_proof).encode()).hexdigest()
            if hash_operation.startswith('0'*self.dificultad_prueba):
                check_proof = True
            else:
                new_proof += 1

        return (new_proof)

    def hash(self, block):
        return hashlib.sha256(str(block).encode('utf-8')).hexdigest()

    def escanear_nodos(self):

        print('Buscando nodos activos en la red...')

        nodos_encontrados = []
        nodos_encontrados.append(self.ip_local)
        puerta_enlace = '192.168.101.'
        inicio = 2
        fin = 255
        contador = inicio+1

        for ip in range(inicio, fin):

            if (hacer_ping(puerta_enlace+str(ip))):
                print(puerta_enlace+str(ip)+':' +
                      PUERTO_BLOCKCHAIN, "encontrado")
                nodos_encontrados.append(puerta_enlace+str(ip))

            print(' ', int(contador*100/fin), '%', end='\r')
            contador += 1

        print('\nEscaneo finalizado.')
        print('Lista de nodos:')
        print(nodos_encontrados)

        return nodos_encontrados

    def validar_cadena(self, cadena):

        print('Validando integridad de la cadena...')

        previous_block = cadena[0]
        block_index = 1

        while block_index < len(cadena):
            bloque = cadena[block_index]
            if bloque['previous_hash'] != self.hash(previous_block):
                print(block_index)
                print(bloque['previous_hash'])
                print(self.hash(previous_block))
                print('Cadena corrupta.')
                return False

            previous_proof = previous_block['proof']
            proof = bloque['proof']

            hash_operation = hashlib.sha256(
                str(previous_proof**2+proof).encode()).hexdigest()

            if not hash_operation.startswith('0'*self.dificultad_prueba):
                print('En la prueba de trabajo')
                print('Cadena corrupta.')
                return False

            previous_block = bloque
            block_index += 1

        print('Cadena validada correctamente.')
        return True

    def repartir_nodos(self):
        for ip in self.peers:
            if ip != self.ip_local:

                try:

                    requests.post(RUTA.format(
                        ip, PUERTO_BLOCKCHAIN, '/actualizar_nodos'), json={'datos': self.peers})

                except:
                    blockchain.peers.remove(ip)


app = Flask(__name__)
app.secret_key = 'secreto'

log = logging.getLogger('werkzeug')
log.disabled = True

blockchain = Blockchain()


@app.route('/verificar_conexion', methods=['GET'])
def verificar_conexion():
    return "Success", 200


@ app.route('/cadena', methods=['GET', 'POST'])
def obtener_cadena():

    if request.method == 'POST':
        blockchain.chain = request.get_json()

        blockchain.transacciones.clear()

        with open('bdJson.json', 'w') as file:
            json.dump(blockchain.chain, file, indent=2)

    return json.dumps(blockchain.chain)


@ app.route('/agregar_transaccion', methods=['POST'])
def agregar_transaccion():

    datos = request.get_json()

    blockchain.transacciones.append(datos)

    for ip in blockchain.peers:
        if ip != blockchain.ip_local:

            try:
                requests.post(RUTA.format(
                    ip, PUERTO_BLOCKCHAIN, '/actualizar_transacciones'), json=blockchain.transacciones)

            except:
                blockchain.peers.remove(ip)

    return "Success", 201


@ app.route('/actualizar_transacciones', methods=['POST'])
# Crea la transacción y la deja lista para ser minada
def actualizar_transacciones():

    nuevas_transacciones = request.get_json()
    blockchain.transacciones = nuevas_transacciones

    return "Success", 201


@app.route('/actualizar_nodos', methods=['POST'])
def actualizar_nodos():

    print('Actualizando nodos...')

    datos = request.get_json()
    blockchain.peers = datos['datos']

    print('Lista de nodos actualizada:')
    print(blockchain.peers)

    return "Success", 201


@ app.route('/', methods=['GET', 'POST'])
@ app.route('/minar', methods=['GET', 'POST'])
# Para minar las transacciones pendientes
def minar():

    if request.method == 'POST':

        actualizado = False

        print('Verificando integridad de la cadena local...')

        if not blockchain.validar_cadena(obtener_cadena_local()):
            print('Integridad de la cadena no conforme, sincronizandose con la red...')

            for ip in blockchain.peers:
                if ip != blockchain.ip_local:
                    try:
                        cadena_remota = obtener_cadena_remota(ip)
                        if blockchain.validar_cadena(cadena_remota):
                            blockchain.chain = cadena_remota

                            with open('bdJson.json', 'w') as file:
                                json.dump(blockchain.chain, file, indent=2)

                            actualizado = True
                            break
                    except:
                        blockchain.peers.remove(ip)

            if not actualizado:
                print('No hay nodos válidos en la red, espere la sincronización.')
                flash('No hay nodos válidos en la red, espere la sincronización.')

                return render_template('minar.html', transacciones=blockchain.transacciones)

        else:

            print('Integridad de la cadena conforme.')

        for transaccion in blockchain.transacciones:
            blockchain.minar_bloque(transaccion['tipo'], transaccion)

        blockchain.transacciones.clear()

        flash('Bloques minados correctamente')

        for ip in blockchain.peers:
            if ip != blockchain.ip_local:

                try:
                    requests.post(RUTA.format(ip, PUERTO_BLOCKCHAIN,
                                              '/cadena'), json=blockchain.chain)
                except:
                    blockchain.peers.remove(ip)

        return render_template('minar.html', transacciones=blockchain.transacciones)

    return render_template('minar.html', transacciones=blockchain.transacciones)


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=int(PUERTO_BLOCKCHAIN), debug=False)
