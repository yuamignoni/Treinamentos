from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_HOST = 'db'
DB_NAME = 'yourdb'
DB_USER = 'youruser'
DB_PASS = 'yourpassword'

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            senha TEXT NOT NULL,
            cargo TEXT NOT NULL
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            emp_id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS treinamentos (
            emp_id TEXT,
            treinamento TEXT,
            validade TEXT,
            PRIMARY KEY (emp_id, treinamento),
            FOREIGN KEY (emp_id) REFERENCES funcionarios (emp_id) ON DELETE CASCADE
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def add_default_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (username, senha, cargo)
        VALUES ('admin', 'admin123', 'Admin')
        ON CONFLICT (username) DO NOTHING;
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def add_fake_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO funcionarios (emp_id, nome, cargo)
        VALUES 
        ('E001', 'Alice', 'Manager'),
        ('E002', 'Bob', 'Developer'),
        ('E003', 'Charlie', 'Designer')
        ON CONFLICT (emp_id) DO NOTHING;
    ''')
    cursor.execute('''
        INSERT INTO treinamentos (emp_id, treinamento, validade)
        VALUES 
        ('E001', 'Leadership', '2024-12-31'),
        ('E002', 'Python Programming', '2023-12-31'),
        ('E003', 'Graphic Design', '2023-06-30')
        ON CONFLICT (emp_id, treinamento) DO NOTHING;
    ''')
    conn.commit()
    cursor.close()
    conn.close()

with app.app_context():
    create_tables()
    add_default_admin()
    add_fake_data()

@app.route('/sync', methods=['GET'])
def sync_get():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    cursor.execute('SELECT * FROM funcionarios')
    funcionarios = cursor.fetchall()
    cursor.execute('SELECT * FROM treinamentos')
    treinamentos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({
        'usuarios': usuarios,
        'funcionarios': funcionarios,
        'treinamentos': treinamentos
    })

@app.route('/sync', methods=['POST'])
def sync_post():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM treinamentos')
    cursor.execute('DELETE FROM funcionarios')
    cursor.execute('DELETE FROM usuarios')
    
    for user in data['usuarios']:
        cursor.execute('''
            INSERT INTO usuarios (username, senha, cargo)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', (user['username'], user['senha'], user['cargo']))
    
    for emp in data['funcionarios']:
        cursor.execute('''
            INSERT INTO funcionarios (emp_id, nome, cargo)
            VALUES (%s, %s, %s)
            ON CONFLICT (emp_id) DO NOTHING
        ''', (emp['emp_id'], emp['nome'], emp['cargo']))
    
    for tr in data['treinamentos']:
        cursor.execute('''
            INSERT INTO treinamentos (emp_id, treinamento, validade)
            VALUES (%s, %s, %s)
            ON CONFLICT (emp_id, treinamento) DO NOTHING
        ''', (tr['emp_id'], tr['treinamento'], tr['validade']))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Sync successful"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
