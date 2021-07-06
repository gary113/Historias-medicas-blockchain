
import matplotlib
import matplotlib.pyplot as plt
from flask import Blueprint, flash, redirect, render_template, request, session

from src.utilidad import (MENSAJE_TRANSACCION, hashear, hashear_contrasenia,
                          nueva_transaccion, obtener_cadena_local)

matplotlib.use('Agg')


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

        flash(MENSAJE_TRANSACCION)
        return redirect('administrador_principal.html')

    elif request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'admin':
            return render_template('registrar_doctor.html')
        else:
            return redirect('administrador.html')


@bp_admin.route('/administrador_principal.html', methods=['GET'])
def administrador_principal():

    cadena = obtener_cadena_local()

    if request.method == 'GET':

        if session.get('usuario') is not None and session['tipo'] == 'admin':

            for bloque in cadena:
                if bloque['transactions']['tipo'] == 0:
                    if bloque['transactions']['usuario'] == session['usuario']:
                        bloque_admin = bloque
                        hash_admin = hashear(bloque_admin)

            return render_template('administrador_principal.html', bloque_admin=bloque_admin, hash_admin=hash_admin)
        else:
            return redirect('administrador.html')


@bp_admin.route('/registrar_administrador.html', methods=['GET', 'POST'])
def registrar_administrador():

    cadena = obtener_cadena_local()

    if request.method == 'POST':

        try:
            if request.form['inputSuper'] == 'Super administrador':
                tipo = 1
            else:
                tipo = 0

        except:
            tipo = 0

        nombres = request.form['inputNombres'].upper()
        apellidos = request.form['inputApellidos'].upper()
        usuario = request.form['inputUsuario']
        contrasenia = hashear_contrasenia(request.form['inputContrasenia'])

        datos = {'tipo': 0, 'super': tipo, 'nombres': nombres,
                 'apellidos': apellidos, 'usuario': usuario, 'contrasenia': contrasenia}

        nueva_transaccion(datos)

        flash(MENSAJE_TRANSACCION)
        return redirect('administrador_principal.html')

    if session.get('usuario') is not None and session['tipo'] == 'admin':

        for bloque in cadena:
            if bloque['transactions']['tipo'] == 0:
                if bloque['transactions']['usuario'] == session['usuario']:
                    bloque_admin = bloque

        return render_template('registrar_administrador.html', tipo_admin=bloque_admin['transactions']['super'])

    else:
        return redirect('administrador.html')


@bp_admin.route('/administrador_estadisticas.html')
def administrador_estadisticas():
    return render_template('administrador_estadisticas.html')


@bp_admin.route('/administrador_estadisticas_topdoctores.html', methods=['GET', 'POST'])
def administrador_pacientesxdoctor_estadisticas():

    top_doctores = []
    cadena = obtener_cadena_local()

    for bloque_doctor in cadena:
        if bloque_doctor['transactions']['tipo'] == 2:
            contador = 0
            hash_doctor = hashear(bloque_doctor['transactions'])
            nombre_completo = bloque_doctor['transactions']['nombres'] + \
                ' ' + bloque_doctor['transactions']['apellidos']
            especialidad_doctor = bloque_doctor['transactions']['especialidad']
            for bloque_historia in cadena:
                if bloque_historia['transactions']['tipo'] == 3 and bloque_historia['transactions']['hash_doctor'] == hash_doctor:
                    contador += 1

            top_doctores.append(
                {'hash_doctor': hash_doctor, 'nombre_completo': nombre_completo, 'especialidad': especialidad_doctor, 'cantidad': contador})

    top_doctores = sorted(
        top_doctores, key=lambda i: i['cantidad'], reverse=True)

    print(top_doctores)

    if request.method == 'POST':

        cantidad_top = request.form['cantidad_top']

        lista_nombres = []
        lista_cantidades = []

        for doctor in top_doctores[:int(cantidad_top)]:
            lista_nombres.insert(0, doctor['nombre_completo'])
            lista_cantidades.insert(0, doctor['cantidad'])

        fig, ax = plt.subplots(figsize=(12, int(cantidad_top)*0.5))
        ax.barh(lista_nombres, lista_cantidades)

        for i, v in enumerate(lista_cantidades):
            ax.text(v+0.1, i, str(v))

        ax.grid(axis='x', zorder=0)
        ax.set_title('Top ' + cantidad_top + ' doctores')
        ax.set(xlabel='Cantidad de pacientes', ylabel='Doctores')

        plt.savefig('static/graficas/grafica_top_doctores.png',
                    format='png', bbox_inches='tight')

        return render_template('administrador_estadisticas_topdoctores.html', top_doctores=top_doctores[:int(cantidad_top)], ruta_imagen='../static/graficas/grafica_top_doctores.png')

    cantidad_top = 5

    lista_nombres = []
    lista_cantidades = []

    for doctor in top_doctores[:cantidad_top]:
        lista_nombres.insert(0, doctor['nombre_completo'])
        lista_cantidades.insert(0, doctor['cantidad'])

    fig, ax = plt.subplots(figsize=(12, cantidad_top*0.5))
    ax.barh(lista_nombres, lista_cantidades)

    for i, v in enumerate(lista_cantidades):
        ax.text(v+0.1, i, str(v))

    ax.grid(axis='x')
    ax.set_title('Top ' + str(cantidad_top) + ' doctores')
    ax.set(xlabel='Cantidad de pacientes', ylabel='Doctores')

    plt.savefig('static/graficas/grafica_top_doctores.png',
                format='png', bbox_inches='tight')

    return render_template('administrador_estadisticas_topdoctores.html', top_doctores=top_doctores[:cantidad_top], ruta_imagen='../static/graficas/grafica_top_doctores.png')


@bp_admin.route('/administrador_estadisticas_topespecialidades.html', methods=['GET', 'POST'])
def administrador_pacientesxespecialidad_estadisticas():
    top_doctores = []
    cadena = obtener_cadena_local()

    for bloque_doctor in cadena:
        if bloque_doctor['transactions']['tipo'] == 2:
            contador = 0
            hash_doctor = hashear(bloque_doctor['transactions'])
            nombre_completo = bloque_doctor['transactions']['nombres'] + \
                ' ' + bloque_doctor['transactions']['apellidos']
            especialidad_doctor = bloque_doctor['transactions']['especialidad']
            for bloque_historia in cadena:
                if bloque_historia['transactions']['tipo'] == 3 and bloque_historia['transactions']['hash_doctor'] == hash_doctor:
                    contador += 1

            top_doctores.append(
                {'hash_doctor': hash_doctor, 'nombre_completo': nombre_completo, 'especialidad': especialidad_doctor, 'cantidad': contador})

    top_especialidades = []

    for doctor in top_doctores:

        conocido = False

        for especialidad in top_especialidades:

            if(especialidad['especialidad'] == doctor['especialidad']):
                especialidad['cantidad'] += doctor['cantidad']

                conocido = True

        if(not conocido):
            linea = {'especialidad': doctor['especialidad'],
                     'cantidad': doctor['cantidad']}
            top_especialidades.append(linea)

    top_especialidades = sorted(
        top_especialidades, key=lambda i: i['cantidad'], reverse=True)

    if request.method == 'POST':

        cantidad_top = request.form['cantidad_top']

        lista_especialidades = []
        lista_cantidades = []

        for especialidad in top_especialidades[:int(cantidad_top)]:
            lista_especialidades.insert(0, especialidad['especialidad'])
            lista_cantidades.insert(0, especialidad['cantidad'])

        fig, ax = plt.subplots(figsize=(12, int(cantidad_top)*0.5))
        ax.barh(lista_especialidades, lista_cantidades)

        for doctor, v in enumerate(lista_cantidades):
            ax.text(v+0.1, doctor, str(v))

        ax.grid(axis='x', zorder=0)
        ax.set_title('Top ' + cantidad_top + ' especialidades')
        ax.set(xlabel='Cantidad de pacientes', ylabel='Especialidades')

        plt.savefig('static/graficas/grafica_top_especialidades.png',
                    format='png', bbox_inches='tight')

        return render_template('administrador_estadisticas_topespecialidades.html', top_especialidades=top_especialidades[:int(cantidad_top)], ruta_imagen='../static/graficas/grafica_top_especialidades.png')

    cantidad_top = 5

    lista_especialidades = []
    lista_cantidades = []

    for especialidad in top_especialidades[:cantidad_top]:
        lista_especialidades.insert(0, especialidad['especialidad'])
        lista_cantidades.insert(0, especialidad['cantidad'])

    fig, ax = plt.subplots(figsize=(12, int(cantidad_top)*0.5))
    ax.barh(lista_especialidades, lista_cantidades)

    for doctor, v in enumerate(lista_cantidades):
        ax.text(v+0.1, doctor, str(v))

    ax.grid(axis='x', zorder=0)
    ax.set_title('Top ' + str(cantidad_top) + ' especialidades')
    ax.set(xlabel='Cantidad de pacientes', ylabel='Especialidades')

    plt.savefig('static/graficas/grafica_top_especialidades.png',
                format='png', bbox_inches='tight')

    return render_template('administrador_estadisticas_topespecialidades.html', top_especialidades=top_especialidades[:cantidad_top], ruta_imagen='../static/graficas/grafica_top_especialidades.png')


@bp_admin.route('/administrador_estadisticas_toplugares.html', methods=['GET', 'POST'])
def administrador_pacientesxlugar_estadisticas():
    top_lugares = []
    cadena = obtener_cadena_local()

    for bloque in cadena:

        conocido = False

        if bloque['transactions']['tipo'] == 3:

            for lugar in top_lugares:
                if(lugar['lugar'] == bloque['transactions']['lugar']):
                    lugar['cantidad'] += 1
                    conocido = True

            if(not conocido):
                linea = {'lugar': bloque['transactions']['lugar'],
                         'cantidad': 1}
                top_lugares.append(linea)

    top_lugares = sorted(
        top_lugares, key=lambda i: i['cantidad'], reverse=True)

    if request.method == 'POST':

        cantidad_top = request.form['cantidad_top']

        lista_lugares = []
        lista_cantidades = []

        for lugar in top_lugares[:int(cantidad_top)]:
            lista_lugares.insert(0, lugar['lugar'])
            lista_cantidades.insert(0, lugar['cantidad'])

        fig, ax = plt.subplots(figsize=(12, int(cantidad_top)*0.5))
        ax.barh(lista_lugares, lista_cantidades)

        for i, v in enumerate(lista_cantidades):
            ax.text(v+0.1, i, str(v))

        ax.grid(axis='x', zorder=0)
        ax.set_title('Top ' + cantidad_top + ' centros médicos')
        ax.set(xlabel='Cantidad de pacientes', ylabel='Centros médicos')

        plt.savefig('static/graficas/grafica_top_lugares.png',
                    format='png', bbox_inches='tight')

        return render_template('administrador_estadisticas_toplugares.html', top_lugares=top_lugares[:int(cantidad_top)], ruta_imagen='../static/graficas/grafica_top_lugares.png')

    cantidad_top = 5

    lista_lugares = []
    lista_cantidades = []

    for lugar in top_lugares[:cantidad_top]:
        lista_lugares.insert(0, lugar['lugar'])
        lista_cantidades.insert(0, lugar['cantidad'])

    fig, ax = plt.subplots(figsize=(12, int(cantidad_top)*0.5))
    ax.barh(lista_lugares, lista_cantidades)

    for i, v in enumerate(lista_cantidades):
        ax.text(v+0.1, i, str(v))

    ax.grid(axis='x', zorder=0)
    ax.set_title('Top ' + str(cantidad_top) + ' centros médicos')
    ax.set(xlabel='Cantidad de pacientes', ylabel='Centros médicos')

    plt.savefig('static/graficas/grafica_top_lugares.png',
                format='png', bbox_inches='tight')

    return render_template('administrador_estadisticas_toplugares.html', top_lugares=top_lugares[:cantidad_top], ruta_imagen='../static/graficas/grafica_top_lugares.png')
