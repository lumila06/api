from flask import Flask, jsonify
from flask_cors import CORS  # Importa CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Habilita CORS en toda la aplicación Flask
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de la base de datos
db_config = {
    'host': 'gestion-base.cz2gmikqglrz.us-east-2.rds.amazonaws.com',
    'user': 'root',
    'password': 'prueba1234',
    'database': 'gestion'
}

@app.route('/requerimientos', methods=['GET'])
def get_requirements():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, sexo, dni, edad, codigo, ubicacion, servicio, medio_transporte, fecha, solicitante FROM requerimientos")
        requirements = cursor.fetchall()
        return jsonify(requirements), 200
    except Error as e:
        print(f"Database error: {e}")  # Imprimir error en la consola
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Error: {e}")  # Imprimir cualquier otro error
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Este es un endpoint de prueba"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Asegúrate de que Flask esté en el puerto 8080
