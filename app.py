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
from flask import Flask,render_template,request, jsonify
import json


class Blockchain:
	
	# This function is created
	# to create the very first
	# block and set it's hash to "0"
	def __init__(self):

		try :
			
			with open('bdJson.json', 'r') as f:

				print('Existe bloque genesis')
				self.chain=json.load(f)

		except:

			self.chain = []

			block = {'index': len(self.chain) + 1,
					'timestamp': str(datetime.datetime.now()),
					'proof': 1,
					'previous_hash': 0}

			self.chain.append(block)

			with open('bdJson.json','w') as file:
				json.dump(self.chain,file,indent=4)


	def create_block_paciente(self, proof, previous_hash,nombre,apellido):
		block = {'index': len(self.chain) + 1,
				'timestamp': str(datetime.datetime.now()),
				'proof': proof,
				'previous_hash': previous_hash,
				'nombre':nombre,
				'apellido':apellido}
		self.chain.append(block)
		return block
	
	def create_block_doctor(self, proof, previous_hash,nombre,apellido):
		block = {'index': len(self.chain) + 1,
				'timestamp': str(datetime.datetime.now()),
				'proof': proof,
				'previous_hash': previous_hash,
				'nombre':nombre,
				'apellido':apellido}
		self.chain.append(block)
		return block
	
	def create_block_registro_historia(self, proof, previous_hash,hash_paciente,hash_doctor):
		block = {'index': len(self.chain) + 1,
				'timestamp': str(datetime.datetime.now()),
				'proof': proof,
				'previous_hash': previous_hash,
				'hash_paciente':hash_paciente,
				'hash_doctor':hash_doctor}
		self.chain.append(block)
		return block

	def minar_bloque(self,tipo_bloque): #1=paciente, 2=doctor , 3=registro_historia

		previous_block = blockchain.chain[-1]
		previous_proof = previous_block['proof']
		proof = blockchain.proof_of_work(previous_proof)
		previous_hash = blockchain.hash(previous_block)

		if tipo_bloque == 1:

			block=blockchain.create_block_paciente(proof, previous_hash,request.form['inputNombre'],request.form['inputApellido'])

		elif tipo_bloque == 2:

			block=blockchain.create_block_doctor(proof, previous_hash,request.form['inputNombre'],request.form['inputApellido'])
		
		elif tipo_bloque == 3:

			block=blockchain.create_block_registro_historia(proof, previous_hash,request.form['inputHashPaciente'],request.form['inputHashDoctor'],datetime.now())

		with open('bdJson.json','r+') as file:
			# First we load existing data into a dict.

			bdJson = json.load(file)
			# Join new_dat3a with file_data
			bdJson.append(block)
			# Sets file's current position at offset.
			file.seek(0)
			# convert back to json.
			json.dump(bdJson, file, indent = 4)

		print(jsonify(block))
		
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
def welcome():
	return render_template('index.html')

@app.route('/registrar_paciente.html', methods=['GET','POST'])
def registrar_paciente():

	if request.method=='POST':

		blockchain.minar_bloque(1)

		return render_template('registrar_paciente.html')
		
	elif request.method=='GET':

		return render_template('registrar_paciente.html')


# Check validity of blockchain
@app.route('/valid', methods=['GET'])
def valid():

	valid = blockchain.chain_valid(blockchain.chain)
	
	if valid:
		response = {'message': 'The Blockchain is valid.'}
	else:
		response = {'message': 'The Blockchain is not valid.'}
	return jsonify(response), 200


# Run the flask server locally
app.run(host='0.0.0.0', port=5000,debug=True)
