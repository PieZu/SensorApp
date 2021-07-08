from flask import Blueprint, request, session, render_template, flash, redirect
from database.config import DATABASE_PATH
import sqlite3
from user.auth import authenticate

def get_all_sensors():
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, name, description, datetime(date_installed, 'unixepoch', 'localtime') as date_installed FROM sensors")
        sensors = cur.fetchall()
    return sensors

def get_sensor_info(id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT name, description, datetime(date_installed, 'unixepoch', 'localtime') as date_installed FROM sensors WHERE id = ?", id)
        name, description, date_installed = cur.fetchone()
    return name, description, date_installed

def insert_new_sensor(name, description, date_installed):
    # internal function to insert new entries in user table
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        if not date_installed is None:
            cur.execute("INSERT INTO sensors (name, description, date_installed) VALUES (?, ?, ?)", (name, description, date_installed))
        else:
            cur.execute("INSERT INTO sensors (name, description) VALUES (?, ?)", (name, description))
        con.commit()
