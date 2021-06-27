from flask import Flask, render_template
from database.createDb import database_bp
from user.auth import user_bp, authenticate
from visualisation.chart import visualisation_bp
from admin.panels import admin_bp
import config
from database.config import DATABASE_PATH

app = Flask(__name__)
app.secret_key = config.secret_key

app.register_blueprint(database_bp)
app.register_blueprint(user_bp)
app.register_blueprint(visualisation_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def hello():
    return render_template("home.html")

@app.route("/sensors")
@authenticate("MANAGE_SENSORS")
def about():
    return render_template("sensors.html")

app.run(debug=True)