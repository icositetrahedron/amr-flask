from flask import Flask, render_template, g
import db

app = Flask(__name__)
db.init_app(app)

@app.route('/')
def index():
    return render_template('annotater.html')
