from flask import Flask, render_template, request, g
import db

app = Flask(__name__)
app.config.from_envvar('AMR_SETTINGS', silent=True)
db.init_app(app)

def get_current_sentence():
    sentence = db.get_db().execute(
        'SELECT id, sentence FROM raw_sentences ORDER BY last_seen DESC LIMIT 0,1'
    ).fetchone()
    if sentence is not None:
        g.current_sentence_id = sentence[0]
        g.current_sentence = sentence[1]

def get_total_sentences():
    sentence = db.get_db().execute(
        'SELECT MAX(id) FROM raw_sentences'
    ).fetchone()
    if sentence is not None:
        g.total_sentences = sentence[0]

def display():
    get_total_sentences()
    words = g.current_sentence.split()
    return render_template('annotater.html', words=words, indices=range(1,len(words)+1))

@app.route('/', methods=('GET', 'POST'))
def index():
    get_current_sentence()
    if request.method == 'POST':
        if "set_sentence" in request.form:
            print("set sentence to: ", request.form["sentence_id"])
            set_current_sentence(request.form["sentence_id"])
    return display()

def set_current_sentence(sentence_id):
    sentence = db.get_db().execute(
        'SELECT sentence FROM raw_sentences WHERE id = ?',
        (sentence_id,)
    ).fetchone()
    print("new sentence: ", sentence[0])
    g.current_sentence_id = sentence_id
    g.current_sentence = sentence[0]
    db.get_db().execute(
        'UPDATE raw_sentences SET last_seen = CURRENT_TIMESTAMP WHERE id = ?',
        (sentence_id,)
    )
    return display()
