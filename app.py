import datetime

from flask import Flask, flash, redirect, render_template, request, session

from Blockchain import Blockchain

app = Flask(__name__)
app.secret_key = 'secreto'

blockchain = Blockchain()


@app.route('/', methods=['GET'])
@app.route('/iniciar_sesion.html', methods=['GET', 'POST'])
def principal():
    if request.method == 'GET':

        #flash('a ver al cine')

        if session.get('usuario') is not None:
            return redirect('menu_principal.html')
        else:
            return render_template('iniciar_sesion.html')

    elif request.method == 'POST':

        usuario = request.form['input_usuario']
        contrasenia = request.form['input_contrasenia']
        hash = request.form['input_hash']

        for bloque in blockchain.chain[1:]:
            if bloque['tipo'] == 2:
                if usuario != "":
                    if bloque['usuario'] == usuario and bloque['contrasenia'] == contrasenia:
                        session['usuario'] = usuario
                        session['contrasenia'] = contrasenia

                        return redirect('menu_principal.html')
                else:

                    if blockchain.hash(bloque) == hash:
                        session['usuario'] = bloque['usuario']
                        session['contrasenia'] = bloque['contrasenia']

                        return redirect('menu_principal.html')

        flash('Credenciales incorrectas')

        return render_template('iniciar_sesion.html')


@app.route('/cerrar_sesion.html', methods=['GET'])
def salir():

    session.clear()
    return redirect('/')


@app.route('/registrar_paciente.html', methods=['GET', 'POST'])
def registrar_paciente():

    if request.method == 'POST':

        dni = request.form['inputDni']

        return redirect('detalle_historia.html?dni='+dni)
        # return render_template('registrar_paciente.html')

    elif request.method == 'GET':

        if session.get('usuario') is not None:
            return render_template('registrar_paciente.html')
        else:
            return redirect('/')


@app.route('/menu_principal.html', methods=['GET', 'POST'])
def menu_principal():

    if request.method == 'POST':

        pass

    elif request.method == 'GET':

        if session.get('usuario') is not None:

            for bloque in blockchain.chain[1:]:
                if bloque['tipo'] == 2:
                    if bloque['usuario'] == session['usuario']:
                        bloque_doctor = bloque
                        hash_doctor = blockchain.hash(bloque_doctor)

            return render_template('menu_principal.html', bloque_doctor=bloque_doctor, hash_doctor=hash_doctor)
        else:
            return redirect('/')


@app.route('/busqueda_paciente.html', methods=['GET', 'POST'])
def busqueda_paciente():

    if request.method == 'POST' and session.get('usuario') is not None:

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

        if session.get('usuario') is not None:
            return render_template('busqueda_paciente.html')
        else:
            return redirect('iniciar_sesion.html')


@app.route('/resultado_busqueda.html', methods=['GET'])
def resultado_busqueda():

    if session.get('usuario') is not None:
        return render_template('resultado_busqueda.html')
    else:
        return redirect('iniciar_sesion.html')


@app.route('/detalle_historia.html', methods=['GET', 'POST'])
def detalle_historia():

    if request.method == 'POST':

        dni = request.args.get('dni')
        # titulo = request.form['inputTitulo']
        # descripcion = request.form['inputDescripcion']

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

        # blockchain.minar_bloque(2, datosAdicionales)
        blockchain.minar_bloque(
            3, hashPaciente=datosAdicionales['hashPaciente'], hashDoctor=datosAdicionales['hashDoctor'])

        return redirect('detalle_historia.html?dni='+dni)

    elif request.method == 'GET':

        if session.get('usuario') is not None:

            dni = request.args.get('dni')
            historia = list()

            for bloque in blockchain.chain[1:]:
                if bloque['tipo'] == 1:
                    if bloque['dni'] == dni:
                        paciente = bloque
                        break

            fecha_nacimiento = paciente['nacimiento'].split('-')

            edad = int((datetime.date.today()-datetime.date(int(fecha_nacimiento[0]), int(
                fecha_nacimiento[1]), int(fecha_nacimiento[2]))).days/365)

            hash_paciente = blockchain.hash(paciente)

            for bloque in blockchain.chain[1:]:
                if bloque['tipo'] == 3:
                    if bloque['hash_paciente'] == hash_paciente:
                        historia.append(bloque)

            return render_template('detalle_historia.html', paciente=paciente, historia=historia, hash_paciente=hash_paciente, edad=edad)

        else:
            return redirect('/')


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

if __name__ == "__main__":

    app.run(host='localhost', port=5000, debug=True)
