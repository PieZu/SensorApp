from flask import Blueprint, request, session, render_template, flash, redirect, Response
from database.config import DATABASE_PATH
import sqlite3
from user.auth import authenticate

def link_user_permission(userID, permissionID):
     with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO user_permissions (user_id, permission_id) VALUES (?, ?)", [userID, permissionID])
        con.commit()

def delink_user_permission(userID, permissionID):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM user_permissions WHERE user_id = ? AND permission_id = ?", [userID, permissionID])
        con.commit()

def user_has_permission(userID, permissionID):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM user_permissions WHERE user_id = ? AND permission_id = ?", [userID, permissionID])
        result = cur.fetchone()
    if result:
        return True
    else: 
        return False

def user_has_permissions(userID, permissionIDs, mode='all'):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        
        # prepepare sql statement with variable amount of ?s
        statement = "SELECT COUNT() FROM user_permissions WHERE user_id = ? AND permission_id IN ("+("?,"*len(permissionIDs))[:-1]+")"
        cur.execute(statement, [userID]+permissionIDs)
        result = cur.fetchone()[0]
        
        if mode == 'any':
            return result > 0
        if mode == 'all':
            return result == len(permissionIDs)
        else:
            return False

def get_user_permissions(userID):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT permission_name FROM user_permissions INNER JOIN permissions ON permissions.id = permission_id WHERE user_id = ?", [userID])
        result = cur.fetchall()
    return result

from api.users import get_userid
from api.permissions import get_permissionid, insert_new_permission
import json

api = Blueprint(
    'userpermapi', __name__,
    template_folder = 'templates',
    url_prefix = '/api/user_permissions'
)

@api.route('/addPermission' , methods=["post"])
@authenticate("MANAGE_PERMISSIONS")
def add_permission():
    userID = get_userid(request.json['username'])
    permissionID = get_permissionid(request.json['permission'])

    if not permissionID:
        permissionID = insert_new_permission(request.json['permission'])
    
    link_user_permission(userID, permissionID)
    return Response(json.dumps(request.json), status=200, mimetype='application/json')

@api.route('/removePermission' , methods=["post"])
@authenticate("MANAGE_PERMISSIONS")
def remove_permission():
    userID = get_userid(request.json['username'])
    permissionID = get_permissionid(request.json['permission'])

    delink_user_permission(userID, permissionID)
    return Response(json.dumps(request.json), status=200, mimetype='application/json')