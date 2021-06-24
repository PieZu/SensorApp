from flask import Blueprint, request, session, render_template, flash, redirect
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

from api.users import get_userid
@authenticate("MANAGE_PERMISSIONS")
def add_permission(username, permission_name):
    userID = get_userid(username)
    permissionID = get_permissionid(permission_name)
    if not permissionID:
        permissionID = insert_new_permission(permission_name)
    link_user_permission(userID, permissionID)

@authenticate("MANAGE_PERMISSIONS")
def remove_permission(username, permission_name):
    userID = get_userid(username)
    permissionID = get_permissionid(permission_name)
    delink_user_permission(userID, permissionID)