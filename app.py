# Python programm to create Blockchain

# For timestamp
import datetime
# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib
# To store data
# in our blockchain
import json

# Flask is for creating the web
# app and jsonify is for
# displaying the blockchain
from flask import Flask, jsonify, redirect, render_template, request


class Blockchain:

    # This function is created
    # to create the very first
    # block and set it's hash to "0"
    def __init__(self):

        try:

            with open('bdJson.json', 'r') as f:

                print('Existe bloque genesis')
                self.chain = json.load(f)

        except:

            self.chain = []

            block = {'index': len(self.chain) + 1,
                     'timestamp': str(datetime.datetime.now()),
                     'proof': 1,
                     'previous_hash': 0}

            self.chain.append(block)

            with open('bdJson.json', 'w') as file:
                json.dump(self.chain, file, indent=4)

    def create_block_paciente(self, proof, previous_hash, nombre, apellido, dni, nacimiento, telefono):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'tipo': 1,
                 'nombre': nombre,
                 'apellido': apellido,
                 'dni': dni,
                 'nacimiento': nacimiento,
                 'telefono': telefono}
        self.chain.append(block)
        return block

    def create_block_doctor(self, proof, previous_hash, nombre, apellido, dni, telefono, usuario, contrasenia):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'tipo': 2,
                 'nombre': nombre,
                 'apellido': apellido,
                 'dni': dni,
                 'telefono': telefono,
                 'usuario': usuario,
                 'contrasenia': contrasenia}
        self.chain.append(block)
        return block

    def create_block_registro_historia(self, proof, previous_hash, hash_paciente, hash_doctor, titulo, descripcion):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'hash_paciente': hash_paciente,
                 'hash_doctor': hash_doctor,
                 'tipo': 3,
                 'titulo': titulo,
                 'descripcion': descripcion}
        self.chain.append(block)
        return block

    # 1=paciente, 2=doctor , 3=registro_historia
    def minar_bloque(self, tipo_bloque, **kwargs):

        previous_block = blockchain.chain[-1]
        previous_proof = previous_block['proof']
        proof = blockchain.proof_of_work(previous_proof)
        previous_hash = blockchain.hash(previous_block)

        if tipo_bloque == 1:

            block = blockchain.create_block_paciente(
                proof, previous_hash, request.form['inputNombre'], request.form['inputApellido'], request.form['inputDni'], request.form['inputNacimiento'], request.form['inputTelefono'])

        elif tipo_bloque == 2:

            block = blockchain.create_block_doctor(
                proof, previous_hash, request.form['inputNombre'], request.form['inputApellido'], request.form['inputDni'], request.form['inputTelefono'], request.form['inputUsuario'], request.form['inputContrasenia'])

            '''
            block = blockchain.create_block_doctor(
                proof, previous_hash, 'Jordi', 'Carranza', '01234567', '996668452', 'jcarranza', 'jcarranza')
            '''

        elif tipo_bloque == 3:

            block = blockchain.create_block_registro_historia(
                proof, previous_hash, kwargs['hashPaciente'], kwargs['hashDoctor'], request.form['inputTitulo'], request.form['inputDescripcion'])

        with open('bdJson.json', 'r+') as file:
            # First we load existing data into a dict.

            bdJson = json.load(file)
            # Join new_dat3a with file_data
            bdJson.append(block)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(bdJson, file, indent=4)

        # print(jsonify(block))

    # This is the function for proof of work
    # and used to successfully mine the block
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[0] == '0':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[0] != '0':
                return False
            previous_block = block
            block_index += 1

        return True


# Creating the Web
# App using flask
app = Flask(__name__)

# Create the object
# of the class blockchain
blockchain = Blockchain()


@app.route('/', methods=['GET'])
@app.route('/iniciar_sesion.html', methods=['GET', 'POST'])
def principal():
    if request.method == 'GET':
        return render_template('iniciar_sesion.html')

    elif request.method == 'POST':
        return redirect('menu_principal.html')


@app.route('/registrar_paciente.html', methods=['GET', 'POST'])
def registrar_paciente():

    if request.method == 'POST':

        blockchain.minar_bloque(1)

        return redirect('menu_principal.html')
        # return render_template('registrar_paciente.html')

    elif request.method == 'GET':

        return render_template('registrar_paciente.html')


@app.route('/menu_principal.html', methods=['GET', 'POST'])
def menu_principal():

    if request.method == 'POST':

        pass

    elif request.method == 'GET':

        return render_template('menu_principal.html')


@app.route('/busqueda_paciente.html', methods=['GET', 'POST'])
def busqueda_paciente():

    if request.method == 'POST':

        nombre = request.form['inputNombre']
        apellido = request.form['inputApellido']
        dni = request.form['inputDni']

        pacientes = list()

        for bloque in blockchain.chain[1:]:
            if bloque['tipo'] == 1:

                if bloque['nombre'] == nombre.upper() and bloque not in pacientes:
                    pacientes.append(bloque)

                if bloque['apellido'] == apellido.upper() and bloque not in pacientes:
                    pacientes.append(bloque)

                if bloque['dni'] == dni and bloque not in pacientes:
                    pacientes.append(bloque)

        return render_template('resultado_busqueda.html', pacientes=pacientes)

    elif request.method == 'GET':

        return render_template('busqueda_paciente.html')


@app.route('/resultado_busqueda.html', methods=['GET', 'POST'])
def resultado_busqueda():

    if request.method == 'POST':

        return render_template('resultado_busqueda.html')

    elif request.method == 'GET':

        return render_template('resultado_busqueda.html')


@app.route('/detalle_historia.html', methods=['GET', 'POST'])
def detalle_historia():

    if request.method == 'POST':

        dni = request.args.get('dni')
        #titulo = request.form['inputTitulo']
        #descripcion = request.form['inputDescripcion']

        for bloque in blockchain.chain[1:]:
            if bloque['tipo'] == 2:
                if bloque['usuario'] == 'jcarranza':
                    doctor = bloque
                    break

        for bloque in blockchain.chain[1:]:
            if bloque['tipo'] == 1:
                if bloque['dni'] == dni:
                    paciente = bloque
                    break

        datosAdicionales = {'hashPaciente': blockchain.hash(
            paciente), 'hashDoctor': blockchain.hash(doctor)}

        #blockchain.minar_bloque(2, datosAdicionales)
        blockchain.minar_bloque(
            3, hashPaciente=datosAdicionales['hashPaciente'], hashDoctor=datosAdicionales['hashDoctor'])

        return redirect('detalle_historia.html?dni='+dni)

    elif request.method == 'GET':

        dni = request.args.get('dni')
        historia = list()

        for bloque in blockchain.chain[1:]:
            if bloque['tipo'] == 1:
                if bloque['dni'] == dni:
                    paciente = bloque
                    break

        hashPaciente = blockchain.hash(paciente)

        for bloque in blockchain.chain[1:]:
            if bloque['tipo'] == 3:
                if bloque['hash_paciente'] == hashPaciente:
                    historia.append(bloque)

        return render_template('detalle_historia.html', paciente=paciente, historia=historia)

# Check validity of blockchain


'''
@app.route('/valid', methods=['GET'])
def valid():

    valid = blockchain.chain_valid(blockchain.chain)

    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}

    return jsonify(response), 200
'''

# Run the flask server locally
app.run(host='0.0.0.0', port=5500, debug=True)
