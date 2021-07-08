from flask import Flask, render_template
from database.createDb import database_bp
from user.auth import user_bp, authenticate, has_perms
from api.users import get_username
from visualisation.chart import visualisation_bp
from admin.panels import admin_bp
import config
from database.config import DATABASE_PATH
from api.blueprints import register_api
# import dummysensors.loop

app = Flask(__name__)
app.secret_key = config.secret_key

app.register_blueprint(database_bp)
app.register_blueprint(user_bp)
app.register_blueprint(visualisation_bp)
app.register_blueprint(admin_bp)
register_api(app)

app.jinja_env.filters["has_permission"] = has_perms
app.jinja_env.filters["get_username"] = get_username

@app.route("/")
def hello():
    return render_template("home.html")

app.run(debug=True)

# TODO: adjust log storage so that it doesnt round to nearest second and udnermine subsecond sensor reading frequencies