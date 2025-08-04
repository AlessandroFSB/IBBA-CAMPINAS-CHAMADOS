from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ibba_secret_key'

def init_db():
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solicitante TEXT,
            setor TEXT,
            tipo TEXT,
            descricao TEXT,
            prioridade TEXT,
            tecnico TEXT,
            status TEXT,
            data_abertura TEXT,
            data_conclusao TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['username'] = username
        session['role'] = user[0]
        return redirect('/dashboard')
    return render_template('login.html', error="Usuário ou senha inválidos")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()
    c.execute('SELECT * FROM chamados')
    chamados = c.fetchall()
    conn.close()
    return render_template('index.html', chamados=chamados, username=session['username'], role=session['role'])

@app.route('/novo', methods=['POST'])
def novo():
    if 'username' not in session:
        return redirect('/')
    dados = (
        request.form['solicitante'],
        request.form['setor'],
        request.form['tipo'],
        request.form['descricao'],
        request.form['prioridade'],
        request.form['tecnico'],
        'Aberto',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        ''
    )
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()
    c.execute("""
        INSERT INTO chamados (
            solicitante, setor, tipo, descricao, prioridade,
            tecnico, status, data_abertura, data_conclusao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, dados)
    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/concluir/<int:id>')
def concluir(id):
    if 'username' not in session or session['role'] != 'tecnico':
        return redirect('/')
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()
    c.execute("""
        UPDATE chamados SET status = ?, data_conclusao = ?
        WHERE id = ?
    """, ('Concluído', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
