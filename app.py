
from flask import Flask

from src.admin import bp_admin
from src.doctor import bp_doctor
from src.sesion import bp_sesion

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

app.run(host="0.0.0.0", port=5000, debug=True)
