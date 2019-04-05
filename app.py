from flask import Flask, render_template, request, g
import db, cmd
from sentence import Sentence

app = Flask(__name__)
app.config.from_envvar('AMR_SETTINGS', silent=True)
db.init_app(app)

def get_current_sentence():
    sentence_row = db.get_db().execute(
        'SELECT id FROM raw_sentences ORDER BY last_seen DESC LIMIT 0,1'
    ).fetchone()
    if sentence_row is not None:
        g.current_sentence = Sentence(sentence_row[0])

def get_total_sentences():
    max_sentence = db.get_db().execute(
        'SELECT MAX(id) FROM raw_sentences'
    ).fetchone()
    if max_sentence is not None:
        g.total_sentences = max_sentence[0]

def display():
    get_total_sentences()
    words = g.current_sentence.words
    return render_template('annotater.html', words=words, indices=range(1,len(words)+1))

@app.route('/', methods=('GET', 'POST'))
def index():
    get_current_sentence()
    if request.method == 'POST':
        if "set_sentence" in request.form:
            g.current_sentence.update_db()
            g.current_sentence = Sentence(request.form["sentence_id"])
        if "add_relation" in request.form:
            #e.g. root :top x18(say)
            #     x18 :arg0 x17
            parse_command(request.form["relation"])
    g.current_sentence.update_last_seen_time()
    return display()


def parse_command(raw_command):
    g.current_sentence.parse_command(raw_command)
    g.last_command = raw_command
