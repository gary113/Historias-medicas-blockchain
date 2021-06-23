from flask import Blueprint, redirect, render_template, request, session

from src.utilidad import (hashear_bloque, hashear_contrasenia,
                          nueva_transaccion, obtener_cadena)

bp_admin = Blueprint('bp_admin', __name__)


@bp_admin.route('/registrar_doctor.html', methods=['GET', 'POST'])
def registrar_doctor():

    if request.method == 'POST':

        nombres = request.form['inputNombres'].upper()
        apellidos = request.form['inputApellidos'].upper()
        dni = request.form['inputDni']
        especialidad = request.form['inputEspecialidad']
        telefono = request.form['inputTelefono']
        usuario = request.form['inputUsuario']
        contrasenia = hashear_contrasenia(request.form['inputContrasenia'])

        datos = {'tipo': 2, 'nombres': nombres, 'apellidos': apellidos,
                 'dni': dni, 'especialidad': especialidad, 'telefono': telefono, 'usuario': usuario, 'contrasenia': contrasenia}

        nueva_transaccion(datos)

        return redirect('administrador_principal.html')

    elif request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'admin':
            return render_template('registrar_doctor.html')
        else:
            return redirect('administrador.html')


@bp_admin.route('/administrador_principal.html', methods=['GET'])
def administrador_principal():

    cadena = obtener_cadena()

    if request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'admin':

            for bloque in cadena:
                if bloque['transactions']['tipo'] == 0:
                    if bloque['transactions']['usuario'] == session['usuario']:
                        bloque_admin = bloque
                        hash_admin = hashear_bloque(bloque_admin)

            return render_template('administrador_principal.html', bloque_admin=bloque_admin, hash_admin=hash_admin)
        else:
            return redirect('administrador.html')
