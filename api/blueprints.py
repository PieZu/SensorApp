from flask import Blueprint
import api.users as users
import api.user_permissions as user_permissions
import api.sensors as sensors
import api.logs as logs
import api.permissions as permissions

def register_api(app):
    app.register_blueprint(users.api)
    app.register_blueprint(user_permissions.api)
    app.register_blueprint(sensors.api)
    app.register_blueprint(logs.api)
    app.register_blueprint(permissions.api)
