

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)

# Habilita CORS en toda la aplicación Flask
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de la base de datos
db_config = {
    'host': os.getenv('DB_HOST', 'gestion-base.cz2gmikqglrz.us-east-2.rds.amazonaws.com'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'prueba1234'),
    'database': os.getenv('DB_NAME', 'gestion')
}

# Función para conectar a la base de datos
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None

# Endpoint para obtener todos los requerimientos
@app.route('/requerimientos', methods=['GET'])
def get_requirements():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, sexo, dni, edad, codigo, ubicacion, servicio, medio_transporte, fecha, solicitante FROM requerimientos")
        requirements = cursor.fetchall()
        return jsonify(requirements), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Endpoint para aceptar un requerimiento y convertirlo en una tarea
@app.route('/requerimientos/<int:id>/aceptar', methods=['POST'])
def accept_requerimiento(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que el requerimiento existe
        cursor.execute("SELECT nombre, apellido, edad, ubicacion, medio_transporte, servicio FROM requerimientos WHERE id = %s", (id,))
        requerimiento = cursor.fetchone()

        if not requerimiento:
            return jsonify({"error": "Requerimiento no encontrado"}), 404

        nombre, apellido, edad, ubicacion, medio_transporte, servicio = requerimiento

        # Convertir ubicacion a cadena y manejar valores nulos
        ubicacion = str(ubicacion) if ubicacion is not None else "Desconocido"

        # Limpiar o sanitizar ubicacion si es necesario (por ejemplo, eliminar caracteres especiales)
        ubicacion = ubicacion.replace("'", "").replace("\"", "")  # Ejemplo de limpieza básica

        # Insertar en la tabla de tareas
        cursor.execute("""
            INSERT INTO tareas (requerimiento_id, estado, nombre, apellido, edad, ubicacion, medio_transporte, servicio)
            VALUES (%s, 'en_proceso', %s, %s, %s, %s, %s,%s)
        """, (id, nombre, apellido, edad, ubicacion, medio_transporte, servicio))

        conn.commit()
        return jsonify({"message": "Requerimiento aceptado y convertido en tarea"}), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint para obtener todas las tareas con su estado
@app.route('/tareas', methods=['GET'])
def get_tasks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, requerimiento_id, inicio_busqueda, inicio_traslado, fin_traslado, ubicacion, medio_transporte, estado, nombre, apellido, edad, servicio FROM tareas")
        tasks = cursor.fetchall()
        
        return jsonify(tasks), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Error en la base de datos"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# Endpoint para actualizar el estado de una tarea
@app.route('/tareas/<int:id>/actualizar', methods=['POST'])
def actualizar_tarea(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Comprobar si el ID no es nulo (esto puede ser redundante porque ya se define como int)
        if id is None:
            return jsonify({"error": "ID no puede ser nulo"}), 400

        # Obtener los datos del cuerpo de la solicitud
        data = request.json
        nuevo_estado = data.get('estado')

        # Verificar que la tarea existe
        cursor.execute("SELECT * FROM tareas WHERE id = %s", (id,))
        tarea = cursor.fetchone()

        if not tarea:
            return jsonify({"error": "Tarea no encontrada"}), 404

        # Actualizar el estado de la tarea
        cursor.execute("UPDATE tareas SET estado = %s WHERE id = %s", (nuevo_estado, id))
        
        conn.commit()
        return jsonify({"message": "Estado de la tarea actualizado"}), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Error en la base de datos"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
