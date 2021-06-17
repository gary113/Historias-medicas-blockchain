
from flask import Flask

from src.Admin import bp_admin
from src.Doctor import bp_doctor
from src.Sesion import bp_sesion

app = Flask(__name__)
app.secret_key = 'secreto'


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

app.register_blueprint(bp_sesion)
app.register_blueprint(bp_doctor)
app.register_blueprint(bp_admin)

app.run(host='localhost', port=5000, debug=True)
