from flask import Flask
from flask import render_template
from flask import send_from_directory

import sqlite3

app = Flask(__name__)


# Otwieranie bazy danych
con = sqlite3.connect('database.db')

# Strona główna
@app.route('/')
def index():
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
    return render_template('home.html')


def create_table_if_needed():
    con.execute('''CREATE TABLE IF NOT EXISTS user
    (id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
    )'''
    )


create_table_if_needed()

if __name__ == '__main__':
    app.run()
