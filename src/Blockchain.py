import datetime
import hashlib
import json


class Blockchain:

    def __init__(self):

        try:

            with open('bdJson.json', 'r') as f:
                self.chain = json.load(f)

        except:

            self.chain = []

            block = {'index': len(self.chain) + 1,
                     'transactions': {
                'tipo': 0,
                'super': 1,
                'nombres': 'Gary',
                'apellidos': 'Candia Nina',
                'usuario': 'gcandia',
                'contrasenia': '7110eda4d09e062aa5e4a390b0a572ac0d2c0220'
            },
                'timestamp': str(datetime.datetime.now()),
                'proof': 1,
                'previous_hash': 0}

            self.chain.append(block)

            with open('bdJson.json', 'w') as file:
                json.dump(self.chain, file, indent=4)

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

        return bloque

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


'''
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
'''

blockchain = Blockchain()
