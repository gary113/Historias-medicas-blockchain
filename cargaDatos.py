import datetime
import hashlib
import json
import random

import pandas as pd

from src.utilidad import (hashear_bloque, nueva_transaccion,
                          obtener_cadena_local)


def cargar_doctores():

    datos_doctores = pd.read_csv('datos/Doctores-Data.csv', encoding='UTF-8')
    for i in datos_doctores.index:

        fila_pandas = dict(datos_doctores.iloc[i])

        nombres = str(fila_pandas['nombres'].upper())
        apellidos = str(fila_pandas['apellidos'].upper())
        dni = str(fila_pandas['dni'])
        especialidad = str(fila_pandas['especialidad'])
        telefono = str(fila_pandas['telefono'])
        usuario = str(fila_pandas['usuario'])
        contrasenia = '7110eda4d09e062aa5e4a390b0a572ac0d2c0220'

        datos = {'tipo': 2, 'nombres': nombres, 'apellidos': apellidos,
                 'dni': dni, 'especialidad': especialidad, 'telefono': telefono, 'usuario': usuario, 'contrasenia': contrasenia}

        nueva_transaccion(datos)


def cargar_pacientes():

    datos_pacientes = pd.read_csv('datos/Pacientes-Data.csv', encoding='UTF-8')
    for i in datos_pacientes.index:

        fila_pandas = dict(datos_pacientes.iloc[i])

        nombres = str(fila_pandas['nombres'].upper())
        apellidos = str(fila_pandas['apellidos'].upper())
        dni = str(fila_pandas['dni'])
        nacimiento = str(fila_pandas['nacimiento'])
        telefono = str(fila_pandas['telefono'])

        datos = {'tipo': 1, 'nombres': nombres, 'apellidos': apellidos,
                 'dni': dni, 'nacimiento': nacimiento, 'telefono': telefono}

        nueva_transaccion(datos)


def generar_hashes_doctores():
    cadena = obtener_cadena_local()
    archivo_hashes_doctores = open('datos/hashes_doctores.csv', 'w')

    # doctores
    for bloque in cadena:
        if bloque['transactions']['tipo'] == 2:
            archivo_hashes_doctores.write(hashear_bloque(bloque)+'\n')

    archivo_hashes_doctores.close()


def generar_hashes_pacientes():
    cadena = obtener_cadena_local()
    archivo_hashes_pacientes = open('datos/hashes_pacientes.csv', 'w')

    # pacientes
    for bloque in cadena:
        if bloque['transactions']['tipo'] == 1:
            archivo_hashes_pacientes.write(hashear_bloque(bloque)+'\n')

    archivo_hashes_pacientes.close()


def proof_of_work(previous_proof):
    new_proof = 1
    check_proof = False

    while check_proof is False:

        hash_operation = hashlib.sha256(
            str(previous_proof**2+new_proof).encode()).hexdigest()
        if hash_operation.startswith('0'*3):
            check_proof = True
        else:
            new_proof += 1

    return (new_proof)


def cargar_historias():

    datos_historias = pd.read_csv('datos/Historias-Data.csv')
    resta_dias = 600

    cadena = obtener_cadena_local()

    for i in datos_historias.index:

        fila_pandas = dict(datos_historias.iloc[i])

        hash_paciente = str(fila_pandas['hash_paciente'])
        hash_doctor = str(fila_pandas['hash_doctor'])
        titulo = str(fila_pandas['titulo'])
        descripcion = str(fila_pandas['descripcion'])
        lugar = str(fila_pandas['lugar'])

        transaction = {'tipo': 3, 'hash_paciente': hash_paciente, 'hash_doctor': hash_doctor,
                       'titulo': titulo, 'descripcion': descripcion, 'lugar': lugar}

        bloque = {'index': len(cadena) + 1,
                  'transactions': transaction,
                  'timestamp': str(datetime.datetime.now()-datetime.timedelta(days=resta_dias)+datetime.timedelta(minutes=random.randint(-180, 180))),
                  'proof': proof_of_work(cadena[-1]['proof']),
                  'previous_hash': hashear_bloque(cadena[-1])
                  }

        cadena.append(bloque)

        with open('bdJson.json', 'r+') as file:

            bd_json = json.load(file)
            bd_json.append(bloque)
            file.seek(0)

            json.dump(bd_json, file, indent=2)

        resta_dias -= 1


# cargar_doctores()
# cargar_pacientes()

# generar_hashes_doctores()
# generar_hashes_pacientes()

# cargar_historias()
