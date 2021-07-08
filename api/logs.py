from flask import Blueprint, request, session, render_template, flash, redirect
from database.config import DATABASE_PATH
import sqlite3

def get_logs_from_sensor(sensor_id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT datetime(timestamp, 'unixepoch', 'localtime'), value FROM log WHERE sensor = ?", [sensor_id])
        logs = cur.fetchall()
    return logs

def get_recent_reading(sensor_id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT datetime(timestamp, 'unixepoch', 'localtime'), value FROM log WHERE sensor = ? ORDER BY timestamp DESC LIMIT 1", [sensor_id])
        log = cur.fetchone()
    return log