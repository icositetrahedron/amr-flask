from flask import Flask, render_template, g
import db

app = Flask(__name__)
app.config.from_envvar('AMR_SETTINGS', silent=True)
db.init_app(app)

@app.route('/')
def index():
    get_current_sentence()
    g.current_sentence = 1
    return render_template('annotater.html')

def get_current_sentence():
    sentence = db.get_db().execute(
        'SELECT id FROM raw_sentences ORDER BY updated DESC LIMIT 0,1'
    ).fetchone()
    print(sentence)
