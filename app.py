from flask import Flask, render_template
from database.createDb import database_bp
from user.auth import user_bp, authenticate
from visualisation.chart import visualisation_bp
from admin.panels import admin_bp
import config
from database.config import DATABASE_PATH
from api.blueprints import register_api
import dummysensors.loop

app = Flask(__name__)
app.secret_key = config.secret_key

app.register_blueprint(database_bp)
app.register_blueprint(user_bp)
app.register_blueprint(visualisation_bp)
app.register_blueprint(admin_bp)
register_api(app)

@app.route("/")
def hello():
    return render_template("home.html")

app.run(debug=True)