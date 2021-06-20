import hashlib

from flask import Blueprint, redirect, render_template, request, session

from src.Blockchain import blockchain

bp_sesion = Blueprint('bp_sesion', __name__)


@bp_sesion.route('/', methods=['GET', 'POST'])
@bp_sesion.route('/iniciar_sesion.html', methods=['GET', 'POST'])
def principal():
    if request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'doctor':
            return redirect('menu_principal.html')
        else:
            return render_template('iniciar_sesion.html')

    elif request.method == 'POST':

        usuario = request.form['input_usuario']
        contrasenia = hashlib.sha1(
            request.form['input_contrasenia'].encode('utf-8')).hexdigest()
        hash = request.form['input_hash']

        for bloque in blockchain.chain[1:]:
            if bloque['transactions']['tipo'] == 2:
                if usuario != "":
                    if bloque['transactions']['usuario'] == usuario and bloque['transactions']['contrasenia'] == contrasenia:
                        session['usuario'] = usuario
                        session['tipo'] = 'doctor'

                        return redirect('menu_principal.html')
                else:

                    if blockchain.hash(bloque) == hash:
                        session['usuario'] = bloque['transactions']['usuario']
                        session['tipo'] = 'doctor'

                        return redirect('menu_principal.html')

        error = 'Credenciales incorrectas'

        return render_template('iniciar_sesion.html', error=error)


@bp_sesion.route('/administrador.html', methods=['GET', 'POST'])
@bp_sesion.route('/administrador', methods=['GET', 'POST'])
def iniciar_administrador():
    if request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'admin':
            return redirect('administrador_principal.html')
        else:
            return render_template('administrador.html')

    elif request.method == 'POST':

        usuario = request.form['input_usuario']
        contrasenia = hashlib.sha1(
            request.form['input_contrasenia'].encode('utf-8')).hexdigest()

        hash = request.form['input_hash']

        for bloque in blockchain.chain:
            if bloque['transactions']['tipo'] == 0:
                if usuario != "":
                    if bloque['transactions']['usuario'] == usuario and bloque['transactions']['contrasenia'] == contrasenia:
                        session['usuario'] = usuario
                        session['tipo'] = 'admin'

                        return redirect('administrador_principal.html')
                else:

                    if blockchain.hash(bloque) == hash:
                        session['usuario'] = bloque['transactions']['usuario']
                        session['tipo'] = 'admin'

                        return redirect('administrador_principal.html')

        error = 'Credenciales incorrectas'

        return render_template('administrador.html', error=error)


@bp_sesion.route('/cerrar_sesion.html', methods=['GET'])
def salir():

    session.clear()
    return redirect('iniciar_sesion.html')
