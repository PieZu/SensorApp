from flask import Blueprint
import api.users as users
import api.user_permissions as user_permissions

def register_api(app):
    app.register_blueprint(users.api)
    app.register_blueprint(user_permissions.api)