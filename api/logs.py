from flask import Blueprint, request, session, render_template, flash, redirect, Response
from user.auth import authenticate
import json
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
    
api = Blueprint(
    'logapi', __name__,
    template_folder = 'templates',
    url_prefix = '/api/logs'
)

@api.route('/<sensor_id>/last/', methods=["GET"])
@authenticate("VIEW_LOGS")
def view_last(sensor_id):
    return Response(json.dumps(get_recent_reading(sensor_id)), status=200, mimetype='application/json')