from flask import Blueprint, request, session, render_template, flash, redirect, Response
from database.config import DATABASE_PATH
import sqlite3
from user.auth import authenticate
import json

def get_all_permissions():
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT permission_name FROM permissions")
        permissions = cur.fetchall()
    return [perm[0] for perm in permissions]

def insert_new_permission(permission_name):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO permissions (permission_name) VALUES (?)", [permission_name])
        con.commit()
    return get_permissionid(permission_name)

def get_permissionid(permission_name):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM permissions WHERE permission_name = ?", [permission_name])
        id = cur.fetchone()
    if id:
        return id[0]
    else: return None

api = Blueprint(
    'permissionsapi', __name__,
    url_prefix = '/api/permissions'
)

@api.route('/', methods=["GET"])
@authenticate("MANAGE_PERMISSIONS")
def dump_permissions():
    return Response(json.dumps(get_all_permissions()), status=200, mimetype='application/json')