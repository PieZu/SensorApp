from flask import Flask, render_template
from database.createDb import database_bp
app = Flask(__name__)

app.register_blueprint(database_bp)

@app.route("/")
def hello():
    return render_template("home.html")
 
@app.route("/sensors")
def about():
    return render_template("sensors.html")

app.run(debug=True)