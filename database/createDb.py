from database.config import DATABASE_PATH, SCHEMA_PATH
from os import path
import sqlite3

if not path.exists(DATABASE_PATH):
    print('no database file detected, creating one.')
    con = sqlite3.connect(DATABASE_PATH)
    
    with open(SCHEMA_PATH) as schema:
        con.executescript(schema.read())
