from flask import Flask, render_template
from database.createDb import database_bp
from user.auth import user_bp, authenticate, has_perms
from api.users import get_username
from visualisation.chart import visualisation_bp
from admin.panels import admin_bp
import config
from database.config import DATABASE_PATH
from api.blueprints import register_api
#import dummysensors.loop 

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

from time import time
from api.logs import insert_logs
from dummysensors.fetch import ph, temp
import math
import sqlite3
@app.route('/fillData/<count>')
def fill(count):
    now = math.floor(time())
    loops = int(count)
    a = [0]*loops
    b = [0]*loops
    for i in range(loops):
        cT = now-i
        a[i] = [cT, temp(cT)]
        b[i] = [cT, ph(cT)]
    insert_logs(1, 1, a)
    insert_logs(1, 2, b)
    return f'added {loops} points of data :D'
@app.route('/clearLogs')
def deleteAll():
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM log")
        con.commit()
    return "deleted __everything__ :oo"

app.run(debug=True)

# TODO: adjust log storage so that it doesnt round to nearest second and udnermine subsecond sensor reading frequencies