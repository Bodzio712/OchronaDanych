# -*- coding: utf-8 -*-
from flask import *
from models.models import *

import uuid
import hashlib
import json
import sqlite3

app = Flask(__name__)
app.secret_key = b'0f\x00#3ZR$1\x18:\x1b\xa3\xe6\xf2\x0fy\xf1\x82\xef\x84P\xe7\xe0'

# Otwieranie bazy danych
conn = sqlite3.connect('database.db')


# Strona główna
@app.route('/')
def index():
    if is_now_logged() == true:
        return render_template('index.html', logged=session['username'])
    return render_template('index.html')


# Logowanie
@app.route('/login')
def login():
    return render_template('login.html')


# Pobieranie loga
@app.route('/icon.png')
def icon():
    return send_from_directory(directory='static', filename='images/icon.png')


# Panel użytwkonika
@app.route('/home')
def home():
    if is_now_logged() == true:
        return render_template('home.html', login=session['username'])
    else:
        return redirect('/login')


# Formularz rejestracji
@app.route('/register')
def register():
    return render_template('register.html')


# Sprawdzanie czy użytkownij jest zalogowany
@app.route('/isLogged', methods=['POST', 'GET'])
def is_logged():
    data = {}
    if is_now_logged() == false:
        data['is_logged'] = 'false'
    else:
        data['is_logged'] = 'true'
        data['username'] = session['username']
    json_data = json.dumps(data)
    return jsonify(json_data)


# Wylogowywanie
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')


# Logowanie użytkownika
@app.route('/loginUser', methods=['POST', 'GET'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('SELECT username, password FROM user')
        data = cur.fetchall()

        for row in data:
            if row[0] == username and match_password_to_databese(password, row[1]):
                session['username'] = username
                return redirect('/')
        return render_template("login.html", messege="Nie ma takiego użytkownika lub hasło niepoprawne")


# Metoda rejestrująca użytkownika
@app.route('/registerUser', methods=['GET', 'POST'])
def register_new_user():
    if request.method == 'POST':
        username = request.form['username']
        passward = request.form['password']
        reapeated_password = request.form['rpassword']

        # Jeśli hasła są takie same
        if passward == reapeated_password:
            # TODO: Dorobić weryfikowanie czy użytkownika nie ma w bazie
            con = engine.connect()
            try:
                user = UserModel()
                # Dodaj uzytwkonika do bazy
                user.register_user(user.find_max_id()+1, username, hash_password(passward))

                # Przekieruj do logowania
                return redirect('/login')
            except Exception as e:
                con.close()
        # Jeśli hasła nie są takie same
        else:
            return "Nieprawidłowe hasło" # TODO: Dorobić żeby wyświetlało się ładnie na stronie


# Sprawdzanie czy użytkownik jest zalogowany
def is_now_logged():
    if 'username' not in session:
        return false
    else:
        return true


# Hashowanie hasła
def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


# Odhashowywanie hasła
def match_password_to_databese(password, hashed_password):
    password_hashed, salt = hashed_password.split(':')
    return password_hashed == hashlib.sha256(salt.encode() + password.encode()).hexdigest()


# Tworzenie tabeli uzytwkoników, jeśli nie została utworzona
def create_table_if_needed():
    conn.execute('''CREATE TABLE IF NOT EXISTS user
    (id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
    )'''
    )

    conn.execute('''CREATE TABLE IF NOT EXISTS note
        (id INTEGER PRIMARY KEY,
        owner TEXT,
        note TEXT,
        is_public BOOL
        )'''
    )

    conn.execute('''CREATE TABLE IF NOT EXISTS access
            (id INTEGER PRIMARY KEY,
            user_id INTEGER,
            note_id INTEGER
            )'''
    )


create_table_if_needed()

if __name__ == '__main__':
    app.run(debug="True", port='5000')
    '''app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
    )'''

# pip install passlib
# pip install sqlalchemy
# pip install peewee
