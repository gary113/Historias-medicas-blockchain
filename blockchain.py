import datetime
import hashlib
import json
import socket

import requests
from flask import Flask, render_template, request
from flask.helpers import flash


class Blockchain:

    def __init__(self):

        self.dificultad_prueba = 3
        self.transacciones = []
        self.peers = []
        self.ip_local = self.conseguir_ip_local()
        #self.ip_local = '192.168.101.8'
        self.chain = []

        self.escanear_nodos()

        # Leer cadena local
        try:

            with open('bdJson.json', 'r') as f:
                self.chain = json.loads(f.read())

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
                    cadena_remota = requests.get(
                        'http://'+ip+':80/cadena').json()

                    if self.validar_cadena(cadena_remota):
                        self.chain = cadena_remota
                        break

            with open('bdJson.json', 'w') as file:
                json.dump(self.chain, file, indent=2)

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

            bdJson = json.load(file)
            bdJson.append(bloque)
            file.seek(0)

            json.dump(bdJson, file, indent=4)

        print('Bloque minado correctamente:')
        print(json.dumps(bloque, indent=1))

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        print('Realizando prueba de trabajo de dificultad ',
              self.dificultad_prueba, ' ...')

        while check_proof is False:

            hash_operation = hashlib.sha256(
                str(previous_proof**2+new_proof).encode()).hexdigest()
            if hash_operation.startswith('0'*self.dificultad_prueba):
                check_proof = True
            else:
                new_proof += 1

        return (new_proof)

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def conseguir_ip_local(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()

        print('Ip local: '+IP)
        return IP

    def escanear_nodos(self):

        puerta_enlace = '192.168.101.1'
        net1 = puerta_enlace.split('.')
        a = '.'

        net2 = net1[0] + a + net1[1] + a + net1[2] + a
        inicio = 2
        fin = 254+1

        for ip in range(inicio, fin):

            ip = net2 + str(ip)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(0.01)

            if (s.connect_ex((ip, 80)) == 0):
                print(ip+':80', "is live")
                self.peers.append(ip)

            s.close()

    def validar_cadena(self, cadena):
        previous_block = cadena[0]
        block_index = 1

        while block_index < len(cadena):
            bloque = cadena[block_index]
            if bloque['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = bloque['proof']

            hash_operation = hashlib.sha256(
                str(previous_proof**2+proof).encode()).hexdigest()

            if not hash_operation.startswith('0'*self.dificultad_prueba):
                return False

            previous_block = bloque
            block_index += 1

        return True


blockchain = Blockchain()

app = Flask(__name__)
app.secret_key = 'secreto'


@app.route('/cadena', methods=['GET', 'POST'])
def obtener_cadena():

    if request.method == 'POST':
        blockchain.chain = request.get_json()

        blockchain.transacciones.clear()

        with open('bdJson.json', 'w') as file:
            json.dump(blockchain.chain, file, indent=2)

    return json.dumps(blockchain.chain)


@app.route('/agregar_transaccion', methods=['POST'])
def agregar_transaccion():

    datos = request.get_json()

    blockchain.transacciones.append(datos)

    for ip in blockchain.peers:
        if ip != blockchain.ip_local:
            requests.post('http://'+ip+'80:/actualizar_transacciones',
                          json=blockchain.transacciones)

    return "Success", 201


@app.route('/actualizar_transacciones', methods=['POST'])
# Crea la transacción y la deja lista para ser minada
def actualizar_transacciones():

    nuevas_transacciones = request.get_json()
    blockchain.transacciones = nuevas_transacciones

    return "Success", 201


@app.route('/', methods=['GET', 'POST'])
@app.route('/minar', methods=['GET', 'POST'])
# Para minar las transacciones pendientes
def minar():

    if request.method == 'POST':

        actualizado = False

        print('Verificando integridad de la cadena local...')

        if not blockchain.validar_cadena(blockchain.chain):
            print('Integridad de la cadena no conforme, sincronizandose con la red...')

            for ip in blockchain.peers:
                if ip != blockchain.ip_local:
                    cadena_remota = requests.get(
                        'http://'+ip+':80/cadena').json()
                    if blockchain.validar_cadena(cadena_remota):
                        blockchain.chain = cadena_remota
                        actualizado = True
                        break

            if not actualizado:
                print('No hay nodos válidos en la red, espere la sincronización.')
                flash('No hay nodos válidos en la red, espere la sincronización.')

                return render_template('minar.html', transacciones=blockchain.transacciones)

        print('Integridad de la cadena conforme.')

        for transaccion in blockchain.transacciones:
            blockchain.minar_bloque(transaccion['tipo'], transaccion)

        blockchain.transacciones.clear()

        flash('Bloques minados correctamente')

        for ip in blockchain.peers:
            if ip != blockchain.ip_local:
                requests.post('http://'+ip+':80/cadena', json=blockchain.chain)

        return render_template('minar.html', transacciones=blockchain.transacciones)

    return render_template('minar.html', transacciones=blockchain.transacciones)


app.run(host="0.0.0.0", port=80, debug=False)
