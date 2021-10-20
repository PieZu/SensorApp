from flask import Blueprint, request, session, render_template, flash, redirect, Response
import json
from database.config import DATABASE_PATH
import sqlite3
from user.auth import authenticate

def get_all_sensors():
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, name, description, datetime(date_installed, 'unixepoch', 'localtime') as date_installed, update_frequency FROM sensors")
        sensors = cur.fetchall()
    return sensors

def get_sensor_info(id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT name, description, datetime(date_installed, 'unixepoch', 'localtime') as date_installed, update_frequency FROM sensors WHERE id = ?", id)
        name, description, date_installed, update_frequency = cur.fetchone()
    return name, description, date_installed, update_frequency

def get_sensor_update_freq(id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT update_frequency FROM sensors WHERE id = ?", (id,))
        update_frequency = cur.fetchone()
    return update_frequency[0]

def update_sensor_metadata(id, name=None, description=None, date_installed=None, update_frequency=None):
    assignment_code = []
    values = []
    if update_frequency is not None:
        update_frequency_num = int(update_frequency) # will throw ValueError if not a number
        assignment_code.append("update_frequency = ?")
        values.append(update_frequency)
    if name is not None: 
        assignment_code.append("name = ?")
        values.append(name)
    if description is not None: 
        assignment_code.append("description = ?")
        values.append(description)
    if date_installed is not None: 
        assignment_code.append("date_installed = ?")
        values.append(date_installed)
    
    assignment_code = ", ".join(assignment_code)

    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("UPDATE sensors SET "+assignment_code+" WHERE id = ?", values+[id])
        con.commit()
    
    return True

def insert_new_sensor(name, description, date_installed):
    # internal function to insert new entries in user table
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        if not date_installed is None:
            cur.execute("INSERT INTO sensors (name, description, date_installed) VALUES (?, ?, ?)", (name, description, date_installed))
        else:
            cur.execute("INSERT INTO sensors (name, description) VALUES (?, ?)", (name, description))
        con.commit()

api = Blueprint(
    'sensorapi', __name__,
    template_folder = 'templates',
    url_prefix = '/api/sensors'
)

@api.route('/', methods=["GET"])
@authenticate()
def view_sensors():
    sensors = [
        {
            "id"                : sensor[0], 
            "name"              : sensor[1], 
            "description"       : sensor[2], 
            "date_installed"    : sensor[3], 
            "update_frequency"  : sensor[4]
        } 
        for sensor in get_all_sensors()
    ]

    return Response(json.dumps(sensors), status=200, mimetype='application/json')


@api.route('/<id>/', methods=["GET"])
@authenticate()
def view_sensor(id):
    sensor = get_sensor_info(id)
    sensor_info = {
        "id"                : id, 
        "name"              : sensor[0], 
        "description"       : sensor[1], 
        "date_installed"    : sensor[2], 
        "update_frequency"  : sensor[3]
    } 

    return Response(json.dumps(sensor_info), status=200, mimetype='application/json')


@api.route('/<id>/', methods=["PATCH"])
@authenticate("MANAGE_SENSORS")
def api_update_sensor_metadata(id):
    data = {}
    data['name'] = data['description'] = data['date_installed'] = data['update_frequency'] = None
    for key,value in request.json.items():
        try:
            data[key] = value
        except KeyError:
            return Response(json.dumps({
                "error": "sensor_updatemeta_keyerror",
                "message": "Unknown property",
                "detail": f"Cannot update sensor for '{key}'='{value}'" +
                          f" as '{key}' is not a known settable property."
            }), status=400, mimetype='application/json')
            
    try:
        update_sensor_metadata(id, name=data['name'], description=data['description'], date_installed=data['date_installed'], update_frequency=data['update_frequency'])
    except ValueError:
        return Response(json.dumps({
            "error": "sensor_updatemeta_freqNaN",
            "message": "Invalid update frequency",
            "detail": f"Cannot set update_frequency of sensor to {data['update_frequency']}" +
                        " as this is in not a valid integer."
        }), status=403, mimetype='application/json')
    return view_sensor(id)