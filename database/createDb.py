from flask import Blueprint, request
from flask import current_app as app

database_bp = Blueprint(
    'database', __name__
)

from database.config import DATABASE_PATH, SCHEMA_PATH
from os import path
import sqlite3

if not path.exists(DATABASE_PATH):
    print('no database file detected, creating one.')
    con = sqlite3.connect(DATABASE_PATH)
    
    with open(SCHEMA_PATH) as schema:
        con.executescript(schema.read())


@database_bp.route('/db', methods=["GET", "POST"])
def display():
    with sqlite3.connect(DATABASE_PATH) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            
            if request.method == "POST":
                cur.execute("INSERT INTO log (sensor, value) VALUES (?, ?)", (request.values.get('sensor'), request.values.get('value')))
            cur.execute("SELECT * FROM log")
            result = cur.fetchall()
            print(result)
            return str(len(result)) + " entries"