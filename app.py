# -*- coding: utf-8 -*-
from flask import *
from models.models import *

import uuid
import hashlib
import json
import sqlite3
import time

app = Flask(__name__)
# Secret key jest potrzebny aby skorzystać z mechanizmu sesji w Flask. Sesja automatycznie wygasa po zamknięciu
app.secret_key = b'0f\x00#3ZR$1\x18:\x1b\xa3\xe6\xf2\x0fy\xf1\x82\xef\x84P\xe7\xe0'

# Otwieranie bazy danych
conn = sqlite3.connect('database.db')


# Tworzenie tabeli uzytwkoników, jeśli nie została utworzona
def create_table_if_needed():
    conn = sqlite3.connect('database.db')
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
        is_public TEXT
        )'''
    )

    conn.execute('''CREATE TABLE IF NOT EXISTS access
            (id INTEGER PRIMARY KEY,
            username INTEGER,
            note_id INTEGER
            )'''
    )
    conn.close()
    conn = sqlite3.connect('database.db')


create_table_if_needed()


# Strona główna
@app.route('/')
def index():
    if is_now_logged() == true:
        try:
            note = NoteModel()
            # Pobierz notatki publiczne
            notes = note.get_all_note()
            # Pobierz notatki prywatne
            x = note.get_priavte_note(session['username'])
            if x != null:
                notes += x
            # Pobierz notatki udostępnione
            x = note.get_shared(session['username'])
            if x!= null:
                notes += x
        except Exception as e:
            notes = null
        return render_template('index.html', logged=session['username'], notes=notes)

    try:
        note = NoteModel()
        notes = note.get_all_note()
    except:
        notes = null

    return render_template('index.html', notes=notes)


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
            con = engine.connect()
            try:
                user = UserModel()
                data = user.check_if_user_exist(username)
                # Sprawdzanie czy użytwkonik już istnieje w bazie
                if data == 1:
                    return "Użytkownik już isnieje"
            except Exception as e:
                con.close()
                return "Błąd w czasie działania aplikacji"

            if len(passward) < 8:
                return "Za krótkie hasło"

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
            return "Nieprawidłowe hasło"


# Dodawanie notatki
@app.route('/addNote', methods=['POST'])
def add_note():
    notes = request.form['note']
    access_username = request.form['visibility']
    try:
        public = request.form['isPublic']
    except:
        public = null

    if public == 'public':
        public = 'true'
    else:
        public = 'false'

    con = engine.connect()

    try:
        note = NoteModel()
        access = AccessModel()
        id_access = access.find_max_id() + 1
        id_note = note.find_max_id() + 1
        # Dodaj uzytwkonika do bazy
        note.add_note(id_note, notes, session['username'], public)
        # Dodaj dostęp gościnny do bazy
        access.add_access(id_access, access_username, id_note)
    except:
        con.close()

    return redirect('/')


# Zmiana hasła
@app.route('/changePassword', methods=['POST'])
def change_password():
    current_password = request.form['currentPassword']
    new_password = request.form['newPassword']
    copy_new_password = request.form['cNewPassword']

    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT username, password FROM user WHERE username = :username", {'username': session['username']})
    data = cur.fetchall()
    con.close()

    for x in data:
        hash = x[1]

    if new_password == copy_new_password and match_password_to_databese(current_password, hash) == True:
        hash = hash_password(new_password)
        user = UserModel()
        user.update_password(session['username'], hash)
        return redirect('/home')

    return redirect('home')


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


# Porówanywanie hasła do zahashowanego hasła
def match_password_to_databese(password, hashed_password):
    # Opóźnienie w czasie weryfiacji hasła w celu wydłużenia ataków
    time.sleep(1)
    password_hashed, salt = hashed_password.split(':')
    return password_hashed == hashlib.sha256(salt.encode() + password.encode()).hexdigest()


if __name__ == '__main__':
    app.run(debug="True", port='5000', ssl_context='adhoc')
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
    )

# pip install passlib
# pip install sqlalchemy
# pip install peewee
