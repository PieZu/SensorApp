from flask import Flask, render_template
import database.createDb
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("home.html")
 
@app.route("/sensors")
def about():
    return render_template("sensors.html")

app.run(debug=True)