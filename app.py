from flask import Flask, jsonify
from flask_cors import CORS  # Importa CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Habilita CORS en toda la aplicación Flask
CORS(app)

# Configuración de la base de datos
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'gestion'
}

@app.route('/requerimientos', methods=['GET'])
def get_requirements():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, sexo, dni, edad, codigo, ubicacion, servicio, medio_transporte,fecha FROM requerimientos")
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

            

if __name__ == '__main__':
    app.run(debug=True, port=8080)
