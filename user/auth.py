from flask import Blueprint, request, session, render_template, flash, redirect
from functools import wraps
from database.config import DATABASE_PATH
import sqlite3
from passlib.hash import sha256_crypt

## classes ##
class InvalidLoginCredentials(Exception):
    # give same error on unknown username as incorrect password for added security
    def __init__(self, message="Invalid Login Credentials"):
        self.message = message
        super().__init__(self.message)

## decorators ##

def authenticate(permission):
    # helper factory for restricting pages to users with certain permission
    # (technically a decorator factory, so that we can pass arguments)
    def decorator(func):
        @wraps(func)
        def secured(*args, **kwargs):
            try:
                user_id = session['userid']
            except KeyError:
                print(f'Guest attempted to access "{func.__name__}"')
                flash('You must be logged in to access this page')
                return redirect('/login')
            permission_id = get_permissionid(permission)
            print(f"user #{session['userid']} attempting to access {func.__name__} needing {permission} ({permission_id}) perms")

            if user_has_permission(user_id, permission_id):
                return func(*args, **kwargs)
            else:
                flash('You do not have permission to access this page.')
                return redirect('/login')
            
        return secured
    return decorator

## flask pages ##
user_bp = Blueprint(
    'user', __name__,
    template_folder = 'templates'
)
@user_bp.route('/login', methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        try:
            id = login(request.values.get('username'), request.values.get('password'))
            session['userid'] = id
            
            redirect('/')
        except InvalidLoginCredentials as error:
            flash(error)
    return render_template('login.html')

## functions ##
def login(username, password):
    with sqlite3.connect(DATABASE_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute("SELECT * FROM users WHERE username = ?",[username])
        user = cur.fetchone()
        cur.close()

        if user:
            # verify password against stored hash
            passwordHash = user['password_hash']
            if sha256_crypt.verify(password, passwordHash):
                return user['id']
            else: 
                # wrong password
                raise InvalidLoginCredentials
        else: 
            # unknown username
            raise InvalidLoginCredentials

def insert_new_user(username, passwordHash):
    # internal function to insert new entries in user table
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", [username, password_hash])
        con.commit()

def insert_new_permission(permission_name):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO permissions (permission_name) VALUES (?)", [permission_name])
        con.commit()
    return get_permissionid(permission_name)

def get_userid(username):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", [username])
        id = cur.fetchone()
    return id[0]

def get_permissionid(permission_name):
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM permissions WHERE permission_name = ?", [permission_name])
        id = cur.fetchone()
    return id[0]

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

@authenticate("CREATE_USERS")
def create_user(username, password):
    # api interfacable authenticated function for admins to add users
    insert_new_user(username, sha256_crypt.hash(str(password)))

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