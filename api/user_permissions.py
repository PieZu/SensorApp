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
    url_prefix = '/api/users/'
)

@api.route('<username>/permissions' , methods=["GET"])
@authenticate("MANAGE_PERMISSIONS")
def view_userperms(username):
    userID = get_userid(username)
    permissions = get_user_permissions(userID)
    return Response(json.dumps([perm[0] for perm in permissions]), status=200, mimetype='application/json')

@api.route('<username>/permissions' , methods=["POST"])
@authenticate("MANAGE_PERMISSIONS")
def add_permission(username):
    user_id = get_userid(username)
    if user_id <= session['userid']:
        return Response(json.dumps({
            "error": "user_perm_creation_admin",
            "message": "Insufficient permission to edit higher user's permission",
            "detail": f"Cannot edit user {username}'s permissions as they have id {user_id}"+
                      f" which is less than own id {session['userid']}."+
                      "\nYou may only edit user accounts created after your own account."
        }), status=403, mimetype='application/json')
    
    permissionID = get_permissionid(request.json['permission'])

    if not permissionID:
        return Response(json.dumps({
            "error": "user_perm_creation_DNE",
            "message": "Unknown permission name",
            "detail": "Cannot add permission '"+request.json['permission']+"' to user '"+username+"' as such a permission does not exist."
        }), status=404)
    
    link_user_permission(user_id, permissionID)
    return Response(json.dumps(request.json), status=200, mimetype='application/json')


@api.route('<username>/permissions/<permission>' , methods=["GET"])
@authenticate("MANAGE_PERMISSIONS")
def view_userperm(username, permission):
    userID = get_userid(username)
    permissionID = get_permissionid(permission)

    return Response(json.dumps({"user":{"username":username,"id":userID},"permission":{"name":permission,"id":permissionID}}), status=200, mimetype='application/json')

@api.route('<username>/permissions/<permission>' , methods=["DELETE"])
@authenticate("MANAGE_PERMISSIONS")
def remove_permission(username, permission):
    user_id = get_userid(username)
    if user_id <= session['userid']:
        return Response(json.dumps({
            "error": "user_perm_deletion_admin",
            "message": "Insufficient permission to edit higher user's permission",
            "detail": f"Cannot edit user {username}'s permissions as they have id {user_id}"+
                      f" which is less than own id {session['userid']}."+
                      "\nYou may only edit user accounts created after your own account."
        }), status=403, mimetype='application/json')
    
    permissionID = get_permissionid(permission)

    delink_user_permission(user_id, permissionID)
    return Response(status=204)