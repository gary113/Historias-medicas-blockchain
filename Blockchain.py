import datetime
import hashlib
import json

from flask import request


class Blockchain:

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

        previous_block = self.chain[-1]
        previous_proof = previous_block['proof']
        proof = self.proof_of_work(previous_proof)
        previous_hash = self.hash(previous_block)

        if tipo_bloque == 1:

            block = self.create_block_paciente(
                proof, previous_hash, request.form['inputNombre'].upper(), request.form['inputApellido'].upper(), request.form['inputDni'], request.form['inputNacimiento'], request.form['inputTelefono'])

        elif tipo_bloque == 2:

            block = self.create_block_doctor(
                proof, previous_hash, request.form['inputNombre'].upper(), request.form['inputApellido'].upper(), request.form['inputDni'], request.form['inputTelefono'], request.form['inputUsuario'], request.form['inputContrasenia'])

            '''
            block = blockchain.create_block_doctor(
                proof, previous_hash, 'Jordi', 'Carranza', '01234567', '996668452', 'jcarranza', 'jcarranza')
            '''

        elif tipo_bloque == 3:

            block = self.create_block_registro_historia(
                proof, previous_hash, kwargs['hashPaciente'], kwargs['hashDoctor'], request.form['inputTitulo'], request.form['inputDescripcion'])

        with open('bdJson.json', 'r+') as file:

            bdJson = json.load(file)
            bdJson.append(block)
            file.seek(0)

            json.dump(bdJson, file, indent=4)

        # print(jsonify(block))

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
