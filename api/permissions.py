from flask import Blueprint, request, session, render_template, flash, redirect
from database.config import DATABASE_PATH
import sqlite3

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