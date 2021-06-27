from flask import Blueprint, request, session, render_template, flash, redirect
from database.config import DATABASE_PATH
import sqlite3
from user.auth import authenticate

def insert_new_user(username, passwordHash):
    # internal function to insert new entries in user table
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", [username, password_hash])
        con.commit()

def get_userid(username):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", [username])
        id = cur.fetchone()
    return id[0]

def get_all_users():
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id, username FROM users")
        results = cur.fetchall()
    return results

@authenticate("CREATE_USERS")
def create_user(username, password):
    # api interfacable authenticated function for admins to add users
    insert_new_user(username, sha256_crypt.hash(str(password)))