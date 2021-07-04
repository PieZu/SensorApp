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

def authenticate(*permissions, mode='all'):
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
                return redirect('/login'), 403

            permission_ids = [get_permissionid(permission_name) if type(permission_name)==str else permission_name for permission_name in permissions]
           
            print(f"user #{session['userid']} attempting to access {func.__name__} needing {mode} of {permissions} perms")
            if user_has_permissions(user_id, permission_ids, mode):
                return func(*args, **kwargs)
            else:
                flash('You do not have permission to access this page.')
                return redirect('/login'), 403

        return secured
    return decorator

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