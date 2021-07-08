from flask import Blueprint, request, render_template
from database.config import DATABASE_PATH, SCHEMA_PATH
from user.config import DEFAULT_USER_KEY
from passlib.hash import sha256_crypt
from os import path
import sqlite3

## imperative code ##
if not path.exists(DATABASE_PATH):
    print('no database file detected, creating one.')
    with sqlite3.connect(DATABASE_PATH) as con:        
        with open(SCHEMA_PATH) as schema:
            con.executescript(schema.read())
        con.execute('UPDATE users SET password_hash = ? WHERE username = "SYSTEM"', [sha256_crypt.hash(DEFAULT_USER_KEY)])

## pages / flask interaction ##
database_bp = Blueprint(
    'database', __name__,
    template_folder = 'templates'
)

# temporary endpoint to add logs
@database_bp.route('/db', methods=["GET", "POST"])
def display():
    with sqlite3.connect(DATABASE_PATH) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            
            if request.method == "POST":
                cur.execute("INSERT INTO log (sensor, value) VALUES (?, ?)", (request.values.get('sensor'), request.values.get('value')))
            return render_template('debug_insert.html')

# temporary endpoint to examine table
@database_bp.route('/table/<string:name>')
def debug(name):
    print(name)
    with sqlite3.connect(DATABASE_PATH) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            
            cur.execute("SELECT * FROM "+name) # this is vulnerable to sql injections but this function is a debug and should be removed anyway
            result = cur.fetchall()
            return render_template('debug_table.html', items=result)

# temporary endpoint to examine table
@database_bp.route('/query/<string:cmd>')
def exec(cmd):
    print(cmd)
    with sqlite3.connect(DATABASE_PATH) as con:
            cur = con.cursor()
            
            cur.execute(cmd) # this is vulnerable to sql injections but this function is a debug and should be removed anyway
            result = con.commit()
            print(result)
            return render_template('debug_table.html')