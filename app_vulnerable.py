# app_vulnerable.py - Aplicación con vulnerabilidades para análisis SonarQube

import pickle
import subprocess
import sqlite3
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================================
# VULNERABILIDAD 1: SQL Injection
# ============================================
@app.route('/user', methods=['GET'])
def get_user():
    """Obtiene información de usuario - VULNERABLE a SQL Injection"""
    user_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # PROBLEMA: Concatenación directa de input del usuario en SQL
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    
    return jsonify(result)


# ============================================
# VULNERABILIDAD 2: Command Injection
# ============================================
@app.route('/ping', methods=['GET'])
def ping_host():
    """Hace ping a un host - VULNERABLE a Command Injection"""
    host = request.args.get('host')
    
    # PROBLEMA: Ejecución de comando shell con input sin validar
    command = f"ping -c 1 {host}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    return jsonify({
        'output': result.stdout,
        'error': result.stderr
    })


# ============================================
# VULNERABILIDAD 3: Deserialización Insegura
# ============================================
@app.route('/load', methods=['POST'])
def load_data():
    """Carga datos serializados - VULNERABLE a Object Injection"""
    data = request.data
    
    # PROBLEMA: Pickle puede ejecutar código arbitrario
    try:
        obj = pickle.loads(data)
        return jsonify({'data': str(obj)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============================================
# VULNERABILIDAD 4: Hard-coded Credentials
# ============================================
# PROBLEMA: Credenciales sensibles en código fuente
DATABASE_URL = "postgresql://admin:SuperSecret123@localhost/mydb"
API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
SECRET_TOKEN = "my-secret-token-12345"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


# ============================================
# VULNERABILIDAD 5: Weak Cryptography
# ============================================
def hash_password(password):
    """Hash de password - VULNERABLE: usa MD5"""
    # PROBLEMA: MD5 es criptográficamente débil
    return hashlib.md5(password.encode()).hexdigest()


@app.route('/register', methods=['POST'])
def register_user():
    """Registra usuario con password hasheado de forma insegura"""
    username = request.json.get('username')
    password = request.json.get('password')
    
    hashed = hash_password(password)
    
    # Guardar en base de datos (simulado)
    return jsonify({
        'username': username,
        'password_hash': hashed
    })


# ============================================
# VULNERABILIDAD 6: Path Traversal
# ============================================
@app.route('/file', methods=['GET'])
def read_file():
    """Lee archivo - VULNERABLE a Path Traversal"""
    filename = request.args.get('name')
    
    # PROBLEMA: Sin validación de ruta, permite acceso a archivos del sistema
    try:
        with open(f"uploads/{filename}", 'r') as f:
            content = f.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============================================
# VULNERABILIDAD 7: XML External Entity (XXE)
# ============================================
import xml.etree.ElementTree as ET

@app.route('/parse-xml', methods=['POST'])
def parse_xml():
    """Parsea XML - VULNERABLE a XXE"""
    xml_data = request.data
    
    # PROBLEMA: Parser XML sin protección contra XXE
    try:
        root = ET.fromstring(xml_data)
        return jsonify({'parsed': ET.tostring(root, encoding='unicode')})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============================================
# VULNERABILIDAD 8: Insufficient Logging
# ============================================
@app.route('/login', methods=['POST'])
def login():
    """Login sin logging adecuado de eventos de seguridad"""
    username = request.json.get('username')
    password = request.json.get('password')
    
    # PROBLEMA: No se loguean intentos fallidos de login
    if username == "admin" and password == SECRET_TOKEN:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Login failed'}), 401


# ============================================
# VULNERABILIDAD 9: Regex DoS (ReDoS)
# ============================================
import re

@app.route('/validate', methods=['POST'])
def validate_input():
    """Validación con regex vulnerable a ReDoS"""
    user_input = request.json.get('data')
    
    # PROBLEMA: Regex con backtracking exponencial
    pattern = r'^(a+)+$'
    
    if re.match(pattern, user_input):
        return jsonify({'valid': True})
    return jsonify({'valid': False})


# ============================================
# VULNERABILIDAD 10: CORS Misconfiguration
# ============================================
@app.after_request
def add_cors_headers(response):
    """CORS mal configurado - permite cualquier origen"""
    # PROBLEMA: Permite acceso desde cualquier dominio
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


if __name__ == '__main__':
    # PROBLEMA ADICIONAL: Debug mode en producción
    app.run(debug=True, host='0.0.0.0')