import datetime

from flask import Blueprint, flash, redirect, render_template, request, session

from src.utilidad import (MENSAJE_TRANSACCION, hashear, nueva_transaccion,
                          obtener_cadena_local)

bp_doctor = Blueprint('bp_doctor', __name__)


@bp_doctor.route('/registrar_paciente.html', methods=['GET', 'POST'])
def registrar_paciente():

    if request.method == 'POST':

        nombres = request.form['inputNombres'].upper()
        apellidos = request.form['inputApellidos'].upper()
        dni = request.form['inputDni']
        nacimiento = request.form['inputNacimiento']
        telefono = request.form['inputTelefono']

        datos = {'tipo': 1, 'nombres': nombres, 'apellidos': apellidos,
                 'dni': dni, 'nacimiento': nacimiento, 'telefono': telefono}

        nueva_transaccion(datos)

        flash(MENSAJE_TRANSACCION)
        return redirect('menu_principal.html')
        # return render_template('registrar_paciente.html')

    elif request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'doctor':
            return render_template('registrar_paciente.html')
        else:
            return redirect('iniciar_sesion.html')


@bp_doctor.route('/menu_principal.html', methods=['GET', 'POST'])
def menu_principal():

    cadena = obtener_cadena_local()

    for bloque in cadena[1:]:

        if bloque['transactions']['tipo'] == 2 and bloque['transactions']['usuario'] == session['usuario']:
            bloque_doctor = bloque
            hash_doctor = hashear(bloque_doctor)

    if request.method == 'POST':

        return render_template('menu_principal.html', bloque_doctor=bloque_doctor, hash_doctor=hash_doctor)

    elif request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'doctor':

            return render_template('menu_principal.html', bloque_doctor=bloque_doctor, hash_doctor=hash_doctor)
        else:
            return redirect('iniciar_sesion.html')


@bp_doctor.route('/busqueda_paciente.html', methods=['GET', 'POST'])
def busqueda_paciente():

    cadena = obtener_cadena_local()

    if request.method == 'POST':

        nombre = request.form['inputNombre']
        apellido = request.form['inputApellido']
        dni = request.form['inputDni']

        pacientes = list()

        for bloque in cadena[1:]:
            if bloque['transactions']['tipo'] == 1:

                if nombre != '' and nombre.upper() in bloque['transactions']['nombres'] and bloque not in pacientes:
                    pacientes.append(bloque)

                if apellido != '' and apellido.upper() in bloque['transactions']['apellidos'] and bloque not in pacientes:
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

    cadena = obtener_cadena_local()

    for bloque in cadena[1:]:
        if bloque['transactions']['tipo'] == 2:
            if bloque['transactions']['usuario'] == session['usuario']:
                doctor = bloque
                break

    hash_doctor = hashear(doctor['transactions'])

    if request.method == 'POST':

        dni = request.args.get('dni')
        indice_filtrar = 0

        if 'btn_registrar' in request.form:

            titulo = request.form['inputTitulo']
            descripcion = request.form['inputDescripcion']
            lugar = request.form['inputLugar']
            estado_ticket = request.form['inputEstado']
            input_indice = request.form['inputIndice']

            for bloque in cadena[1:]:
                if bloque['transactions']['tipo'] == 1:
                    if bloque['transactions']['dni'] == dni:
                        paciente = bloque
                        break

            hash_paciente = hashear(paciente['transactions'])

            if input_indice == 'Nuevo ticket':

                indice_historia = 1

                for bloque in cadena[::-1]:
                    if bloque['transactions']['tipo'] == 3 and bloque['transactions']['hash_paciente'] == hash_paciente:
                        indice_historia = bloque['transactions']['indice_ticket']+1
                        break

            else:
                indice_historia = int(input_indice.split('-')[0])

            datos = {'tipo': 3, 'indice_ticket': indice_historia, 'estado_ticket': estado_ticket, 'hash_paciente': hash_paciente, 'hash_doctor': hash_doctor,
                                'titulo': titulo, 'descripcion': descripcion, 'lugar': lugar}

            nueva_transaccion(datos)

            flash(MENSAJE_TRANSACCION)

        elif 'btn_filtrar' in request.form:
            indice_filtrar = request.form['inputFiltrar'].split('-')[0]

            if indice_filtrar == 'Sin filtro':
                return redirect('detalle_historia.html?dni='+dni+'&indice='+str(0))
            else:
                return redirect('detalle_historia.html?dni='+dni+'&indice='+str(indice_filtrar))

        return redirect('detalle_historia.html?dni='+dni+'&indice='+str(indice_filtrar))

    if session.get('usuario') is not None and session['tipo'] == 'doctor':

        lineasHistoria = []
        dni = request.args.get('dni')
        indice_filtrar = int(request.args.get('indice'))

        for bloque in cadena[1:]:
            if bloque['transactions']['tipo'] == 1:
                if bloque['transactions']['dni'] == dni:
                    paciente = bloque
                    break

        hash_paciente = hashear(paciente['transactions'])

        fecha_nacimiento = paciente['transactions']['nacimiento'].split(
            '-')

        edad = int((datetime.date.today()-datetime.date(int(fecha_nacimiento[0]), int(
            fecha_nacimiento[1]), int(fecha_nacimiento[2]))).days/365)

        lista_indices_abiertos = []
        lista_indices_cerrados = []
        lista_indices_totales = []
        lista_casos_totales = ['Sin filtro']
        lista_casos = ['Nuevo ticket']

        for bloque in cadena[1:]:
            if indice_filtrar == 0:
                if bloque['transactions']['tipo'] == 3:
                    if bloque['transactions']['hash_paciente'] == hash_paciente:
                        lineasHistoria.append(bloque)
            else:
                if bloque['transactions']['tipo'] == 3 and bloque['transactions']['indice_ticket'] == indice_filtrar:
                    if bloque['transactions']['hash_paciente'] == hash_paciente:
                        lineasHistoria.append(bloque)

        for bloque in cadena[::-1]:

            if bloque['transactions']['tipo'] == 3 and bloque['transactions']['indice_ticket'] not in lista_indices_abiertos and bloque['transactions']['indice_ticket'] not in lista_indices_cerrados:

                if bloque['transactions']['estado_ticket'] == 'Abierto':
                    lista_indices_abiertos.append(
                        bloque['transactions']['indice_ticket'])

                    lista_casos.append(str(bloque['transactions']['indice_ticket']) + ' - ' +
                                       bloque['transactions']['titulo'] + ' - ' + bloque['timestamp'][:16])
                else:
                    lista_indices_cerrados.append(
                        bloque['transactions']['indice_ticket'])

        for bloque in cadena[1:]:
            if bloque['transactions']['tipo'] == 3 and bloque['transactions']['indice_ticket'] not in lista_indices_totales:
                lista_indices_totales.append(
                    bloque['transactions']['indice_ticket'])
                lista_casos_totales.append(str(bloque['transactions']['indice_ticket']) + ' - ' +
                                           bloque['transactions']['titulo'] + ' - ' + bloque['timestamp'][:16])

        for linea in lineasHistoria:

            linea['timestamp'] = linea['timestamp'][:16]

            for bloque in cadena[1:]:
                if bloque['transactions']['tipo'] == 2:
                    if linea['transactions']['hash_doctor'] == hashear(bloque['transactions']):
                        linea['transactions']['nombres_apellidos_doctor'] = bloque['transactions']['nombres'] + \
                            ' ' + bloque['transactions']['apellidos']
                        linea['transactions']['especialidad_doctor'] = bloque['transactions']['especialidad']
                        break

        return render_template('detalle_historia.html', lista_casos_totales=lista_casos_totales, lista_casos=lista_casos, paciente=paciente, historia=lineasHistoria, hash_paciente=hash_paciente, edad=edad)

    else:
        return redirect('iniciar_sesion.html')
