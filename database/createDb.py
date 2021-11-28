from flask import Blueprint, request, render_template
from database.config import DATABASE_PATH, SCHEMA_PATH, DUMMY_DATA_AMOUNT
from user.config import DEFAULT_USER_KEY
from passlib.hash import sha256_crypt
from os import path
import sqlite3
from time import time
from api.logs import insert_logs
from dummysensors.fetch import ph, temp
import math

## imperative code ##
if not path.exists(DATABASE_PATH):
    # create database
    print('no database file detected, creating one.')
    with sqlite3.connect(DATABASE_PATH) as con:        
        with open(SCHEMA_PATH) as schema:
            con.executescript(schema.read())
        con.execute('UPDATE users SET password_hash = ? WHERE username = "SYSTEM"', [sha256_crypt.hash(DEFAULT_USER_KEY)])

    # fill dummy data
    now = math.floor(time())
    loops = int(DUMMY_DATA_AMOUNT)
    a = [0]*loops
    b = [0]*loops
    for i in range(loops):
        cT = now-i*3
        a[i] = [cT, temp(cT)]
        b[i] = [cT, ph(cT)]
    insert_logs(1, 1, a)
    insert_logs(1, 2, b)
    print(f'added {loops} points of data :D')

## pages / flask interaction ##
database_bp = Blueprint(
    'database', __name__,
    template_folder = 'templates'
)