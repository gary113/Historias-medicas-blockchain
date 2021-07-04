
from flask import Flask

from src.admin import bp_admin
from src.doctor import bp_doctor
from src.sesion import bp_sesion

app = Flask(__name__)
app.secret_key = 'secreto'

app.register_blueprint(bp_sesion)
app.register_blueprint(bp_doctor)
app.register_blueprint(bp_admin)

if __name__ == '__main__':

    app.run(host="localhost", port=5000, debug=True)
