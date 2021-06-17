import datetime

from flask import Blueprint, redirect, render_template, request, session

from src.Blockchain import blockchain

bp_doctor = Blueprint('bp_doctor', __name__)


@bp_doctor.route('/registrar_paciente.html', methods=['GET', 'POST'])
def registrar_paciente():

    if request.method == 'POST':

        nombres = request.form['inputNombres'].upper()
        apellidos = request.form['inputApellidos'].upper()
        dni = request.form['inputDni']
        nacimiento = request.form['inputNacimiento']
        telefono = request.form['inputTelefono']

        datos = {'nombres': nombres, 'apellidos': apellidos,
                 'dni': dni, 'nacimiento': nacimiento, 'telefono': telefono}

        blockchain.minar_bloque(1, datos)

        return redirect('detalle_historia.html?dni='+dni)
        # return render_template('registrar_paciente.html')

    elif request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'doctor':
            return render_template('registrar_paciente.html')
        else:
            return redirect('iniciar_sesion.html')


@bp_doctor.route('/menu_principal.html', methods=['GET', 'POST'])
def menu_principal():

    if request.method == 'POST':

        pass

    elif request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'doctor':

            for bloque in blockchain.chain[1:]:

                if bloque['transactions']['tipo'] == 2 and bloque['transactions']['usuario'] == session['usuario']:
                    bloque_doctor = bloque
                    hash_doctor = blockchain.hash(bloque_doctor)

            return render_template('menu_principal.html', bloque_doctor=bloque_doctor, hash_doctor=hash_doctor)
        else:
            return redirect('iniciar_sesion.html')


@bp_doctor.route('/busqueda_paciente.html', methods=['GET', 'POST'])
def busqueda_paciente():

    if request.method == 'POST':

        nombre = request.form['inputNombre']
        apellido = request.form['inputApellido']
        dni = request.form['inputDni']

        pacientes = list()

        for bloque in blockchain.chain[1:]:
            if bloque['transactions']['tipo'] == 1:

                if nombre.upper() in bloque['transactions']['nombres'] and bloque not in pacientes:
                    pacientes.append(bloque)

                if apellido.upper() in bloque['transactions']['apellidos'] and bloque not in pacientes:
                    pacientes.append(bloque)

                if bloque['transactions']['dni'] == dni and bloque not in pacientes:
                    pacientes.append(bloque)

        return render_template('resultado_busqueda.html', pacientes=pacientes)

    elif request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'doctor':
            return render_template('busqueda_paciente.html')
        else:
            return redirect('iniciar_sesion.html')


@bp_doctor.route('/resultado_busqueda.html', methods=['GET'])
def resultado_busqueda():

    if session.get('usuario') is not None and session['tipo'] == 'doctor':
        return render_template('resultado_busqueda.html')
    else:
        return redirect('iniciar_sesion.html')


@bp_doctor.route('/detalle_historia.html', methods=['GET', 'POST'])
def detalle_historia():

    for bloque in blockchain.chain[1:]:
        if bloque['transactions']['tipo'] == 2:
            if bloque['transactions']['usuario'] == session['usuario']:
                doctor = bloque
                break

    hash_doctor = blockchain.hash(doctor)

    if request.method == 'POST':

        titulo = request.form['inputTitulo']
        descripcion = request.form['inputDescripcion']
        lugar = request.form['inputLugar']
        dni = request.args.get('dni')

        for bloque in blockchain.chain[1:]:
            if bloque['transactions']['tipo'] == 1:
                if bloque['transactions']['dni'] == dni:
                    paciente = bloque
                    break

        hash_paciente = blockchain.hash(paciente)

        datosAdicionales = {'hash_paciente': hash_paciente, 'hash_doctor': hash_doctor,
                            'titulo': titulo, 'descripcion': descripcion, 'lugar': lugar}

        blockchain.minar_bloque(3, datosAdicionales)

        return redirect('detalle_historia.html?dni='+dni)

    elif request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'doctor':

            lineasHistoria = list()
            dni = request.args.get('dni')

            for bloque in blockchain.chain[1:]:
                if bloque['transactions']['tipo'] == 1:
                    if bloque['transactions']['dni'] == dni:
                        paciente = bloque
                        break

            hash_paciente = blockchain.hash(paciente)
            fecha_nacimiento = paciente['transactions']['nacimiento'].split(
                '-')

            edad = int((datetime.date.today()-datetime.date(int(fecha_nacimiento[0]), int(
                fecha_nacimiento[1]), int(fecha_nacimiento[2]))).days/365)

            for bloque in blockchain.chain[1:]:
                if bloque['transactions']['tipo'] == 3:
                    if bloque['transactions']['hash_paciente'] == hash_paciente:
                        lineasHistoria.append(bloque)

            for linea in lineasHistoria:

                linea['timestamp'] = linea['timestamp'][:16]

                for bloque in blockchain.chain[1:]:
                    if bloque['transactions']['tipo'] == 2:
                        if linea['transactions']['hash_doctor'] == blockchain.hash(bloque):
                            linea['transactions']['nombres_apellidos_doctor'] = bloque['transactions']['nombres'] + \
                                ' ' + bloque['transactions']['apellidos']
                            linea['transactions']['especialidad_doctor'] = bloque['transactions']['especialidad']
                            break

            return render_template('detalle_historia.html', paciente=paciente, historia=lineasHistoria, hash_paciente=hash_paciente, edad=edad)

        else:
            return redirect('iniciar_sesion.html')
