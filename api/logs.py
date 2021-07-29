from flask import Blueprint, request, session, render_template, flash, redirect, Response
from user.auth import authenticate
import json
from database.config import DATABASE_PATH
import sqlite3
from time import time
from api.sensors import get_sensor_update_freq, get_all_sensors

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

def insert_log(user_id, sensor_id, timestamp, value):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO log (sensor, timestamp, value, source_user) VALUES (?, ?, ?, ?)", (sensor_id, timestamp, value, user_id))
        con.commit()
        return cur.lastrowid

def insert_logs(user_id, sensor_id, logs):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.executemany("INSERT INTO log (source_user, sensor, timestamp, value) VALUES (?, ?, ?, ?)", ([user_id, sensor_id]+log for log in logs))
        con.commit()
    return True

def dump_logs():
    sensors = [name for _,name,_,_,_ in get_all_sensors()]
    table = []
    row_length = range(len(sensors)+1)

    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT datetime(timestamp, 'unixepoch', 'localtime'), sensor, value FROM log ORDER BY timestamp ASC")

        last_timestamp = None
        last_row = []
        for (timestamp, sensor, value) in cur:
            # print(timestamp, sensor, value)
            if not timestamp == last_timestamp:
                table.append(last_row)
                last_row = list(row_length)
                last_row[0] = timestamp
                last_timestamp = timestamp
            last_row[sensor] = value
        table.append(last_row)
    table[0] = ["Time"]+sensors
    return table

api = Blueprint(
    'logapi', __name__,
    template_folder = 'templates',
    url_prefix = '/api/logs'
)


COMMA = ','
QUOTE = '"'
TWO_QUOTES = '""'
@api.route('/dump')
@authenticate("VIEW_LOGS")
def get_csv():
    table = dump_logs()
    # first row is sensor names wrapped in "", with " marks escaped with ""
    csv = COMMA.join(QUOTE+ name.replace(QUOTE, TWO_QUOTES) +QUOTE  for name in table[0])
    for row in table[1:]:
        csv += "\n" + COMMA.join(str(value) for value in row)
    response = Response(csv, status=200, mimetype='text/csv')
    response.headers['Content-Disposition'] = 'inline; filename="log_data.csv"'
    return response

@api.route('/<sensor_id>/last/', methods=["GET"])
@authenticate("VIEW_LOGS")
def view_last(sensor_id):
    return Response(json.dumps(get_recent_reading(sensor_id)), status=200, mimetype='application/json')

@api.route('/<sensor_id>/', methods=["GET"])
@authenticate("VIEW_LOGS")
def view_all(sensor_id):
    return Response(json.dumps(get_logs_from_sensor(sensor_id)), status=200, mimetype='application/json')

@api.route('/<sensor_id>/', methods=["POST"])
@authenticate("ADD_LOGS")
def add_log(sensor_id):
    if type(request.json) == list:
        if type(request.json[1]) == int:
            timestamp,value = request.json
        else:
            if type(request.json[1]) == list:
                insert_logs(session['userid'], sensor_id, request.json)
            if type(request.json[1]) == dict:
                insert_logs(session['userid'], sensor_id, ([log['timestamp'], log['value']] for log in request.json))
            return Response(get_sensor_update_freq(sensor_id), status=200)
    
    if type(request.json) == dict:
        value = request.json['value']
        if 'timestamp' in request.json:
            timestamp = request.json['timestamp']
        else:
            timestamp = round(time()*1000)
        
    insert_log(session['userid'], sensor_id, value, timestamp)
    return Response(get_sensor_update_freq(sensor_id), status=200)