from flask import Blueprint, request, session, render_template, flash, redirect, Response
from database.config import DATABASE_PATH
import sqlite3
from user.auth import authenticate
from passlib.hash import sha256_crypt
import json

## classes ##
class UnknownUsernameError(Exception):
    def __init__(self, username):
        self.response = Response(json.dumps({
            "error": "user_getid_unknownusername",
            "message": "Unknown username",
            "detail": f"Could not locate user with username '{username}', perhaps their account has been deleted, or perhaps it never existed, perhaps it was all an illusion."
        }), status=404, mimetype='application/json')
        
        super().__init__(self.response)

def insert_new_user(username, password_hash):
    # internal function to insert new entries in user table
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", [username, password_hash])
        con.commit()
        inserted_rowid = cur.lastrowid
    return inserted_rowid

def get_userid(username):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", [username])
        id = cur.fetchone()
    if not id:
        raise UnknownUsernameError(username)
    return id[0]

def get_username(userid):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT username FROM users WHERE id = ?", [userid])
        name = cur.fetchone()
    return name[0]

def get_user_info(user_id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, username FROM users WHERE id = ?", [user_id])
        info = cur.fetchone()
    return info

def get_all_users():
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, username FROM users ORDER BY id")
        results = cur.fetchall()
    return results

def delete_user(id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", [id])
        cur.execute("DELETE FROM user_permissions WHERE user_id = ?", [id])

api = Blueprint(
    'userapi', __name__,
    template_folder = 'templates',
    url_prefix = '/api'
)


@api.route('/users/', methods=["GET"])
@authenticate()
def view_users():
    # api interfacable authenticated function for admins to add users
    users = get_all_users()
    return Response(json.dumps([{'id':row[0], 'username':row[1]} for row in users]), status=200, mimetype='application/json')

@api.route('/users/', methods=["POST"])
@authenticate("CREATE_USERS")
def create_user():
    # api interfacable authenticated function for admins to add users
    if request.json['username'] == '':
        return Response(json.dumps({
            "error": "user_create_blank",
            "message": "Enter a username",
            "detail": "Cannot create user with blank username."
        }), status=400, mimetype='application/json')
    if '/' in request.json['username']:
        return Response(json.dumps({
            "error": "user_create_invalid",
            "message": "Invalid username",
            "detail": "Username cannot contain slashes."
        }), status=400, mimetype='application/json')
    try:
        new_row = insert_new_user(request.json['username'], sha256_crypt.hash(str(request.json['password'])) )
        inserted = get_user_info(new_row)
        return Response(json.dumps({'id':inserted[0], 'username':inserted[1]}), status=200, mimetype='application/json')
    except sqlite3.IntegrityError:
        return Response(json.dumps({
            "error": "user_create_duplicate",
            "message": "Username in use",
            "detail": "Cannot create user with username '"+request.json['username']+"' as such an account already exists."
        }), status=400, mimetype='application/json')

@api.route('/users/<username>', methods=["GET"])
@authenticate()
def view_user(username):
    try:
        user_id = get_userid(username)
    except UnknownUsernameError as error:
        return error.response
    return Response(json.dumps({"id":user_id, "username":username}), status=200, mimetype='application/json')

@api.route('/users/<username>', methods=["DELETE"])
@authenticate("DELETE_USERS")
def destroy_user(username):
    try:
        user_id = get_userid(username)
    except UnknownUsernameError as error:
        return error.response
    if user_id <= session['userid']:
        return Response(json.dumps({
            "error": "user_delete_admin",
            "message": "Insufficient permission to delete higher user",
            "detail": f"Cannot delete user {username} as they have id {user_id}"+
                      f" which is less than own id {session['userid']}."+
                      "\nYou may only delete user accounts created after your own account."
        }), status=403, mimetype='application/json')
    delete_user(user_id)
    return Response(status=204)