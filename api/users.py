from flask import Blueprint, request, session, render_template, flash, redirect, Response
from database.config import DATABASE_PATH
import sqlite3
from user.auth import authenticate
from passlib.hash import sha256_crypt
import json

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
    return id[0]

def get_user_info(user_id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, username FROM users WHERE id = ?", [user_id])
        info = cur.fetchone()
    return info

def get_all_users():
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, username FROM users")
        results = cur.fetchall()
    return results

def delete_user(id):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", [id])

api = Blueprint(
    'userapi', __name__,
    template_folder = 'templates',
    url_prefix = '/api/users'
)

@api.route('/createUser', methods=["post"])
@authenticate("CREATE_USERS")
def create_user():
    # api interfacable authenticated function for admins to add users
    new_row = insert_new_user(request.json['username'], sha256_crypt.hash(str(request.json['username'])) )
    inserted = get_user_info(new_row)
    return Response(json.dumps({'id':inserted[0], 'username':inserted[1]}), status=200, mimetype='application/json')


@api.route('/deleteUser', methods=["post"])
@authenticate("DELETE_USERS")
def destroy_user():
    user_id = get_userid(request.json['username'])
    delete_user(user_id)
    return Response(json.dumps(request.json), status=200, mimetype='application/json')