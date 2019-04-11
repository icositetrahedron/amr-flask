import pickle
from flask import Flask, render_template, request, g, redirect, url_for
import db, cmd
from sentence import Sentence

app = Flask(__name__)
app.config.from_envvar('AMR_SETTINGS', silent=True)
db.init_app(app)

def set_sentences(sentences):
    sentences_pickle = open("sentences.pickle","wb")
    pickle.dump(sentences, sentences_pickle)
    sentences_pickle.close()

def get_sentences():
    try:
        return pickle.load(open("sentences.pickle","rb"))
    except:
        max_sentence = db.get_db().execute(
            'SELECT MAX(id) FROM raw_sentences'
        ).fetchone()
        if max_sentence is not None:
            total_sentences = max_sentence[0]
        sentences = list(map(lambda id: Sentence(id), range(1, total_sentences+1)))
        sentences_pickle = open("sentences.pickle","wb")
        pickle.dump(sentences, sentences_pickle)
        sentences_pickle.close()
        return sentences

def set_current_sentence_id(id):
    id = int(id)
    id_pickle = open("current_sentence_id.pickle","wb")
    pickle.dump(id, id_pickle)
    id_pickle.close()
    get_sentences()[id-1].update_last_seen_time()
    get_sentences()[id-1].update_db()

def get_current_sentence_id():
    try:
        return int(pickle.load(open("current_sentence_id.pickle","rb")))
    except:
        sentence_row = db.get_db().execute(
            'SELECT id FROM raw_sentences ORDER BY last_seen DESC LIMIT 0,1'
        ).fetchone()
        if sentence_row is not None:
            return int(sentence_row[0])
        else:
            return 1

def get_current_sentence():
    return get_sentences()[get_current_sentence_id()-1]


def words_to_colors():
    colors = dict()
    for index in range(1, len(get_current_sentence().words)+1):
        colors[index] = "red" if index in get_current_sentence().annotated_indices else "blue"
    return colors

def display():
    sentence = get_current_sentence()
    num_words = len(sentence.words)
    node_indices = range(len(sentence.nodes_as_list()))
    return render_template('annotater.html',
                           sentence=sentence,
                           indices=range(num_words),
                           colors=words_to_colors(),
                           node_indices=node_indices,
                           total_sentences=len(get_sentences()))

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        if "set_sentence" in request.form:
            set_current_sentence_id(request.form["sentence_id"])
        if "add_relation" in request.form:
            #e.g. root :top x18(say)
            #     x18 :arg0 x17
            parse_command(request.form["relation"])
    return display()

def parse_command(raw_command):
    sentences = get_sentences()
    try:
        sentences[get_current_sentence_id()-1].parse_command(raw_command)
        set_sentences(sentences)
        g.last_command = raw_command
    except:
        g.last_command = raw_command + " (invalid input)"

@app.route('/delete_node/<node_index>', methods=['GET', 'POST'])
def delete_node(node_index):
    node_index = int(node_index)
    sentences = get_sentences()
    sentence = sentences[get_current_sentence_id()-1]
    sentence.delete_node(node_index)
    set_sentences(sentences)
    g.last_command = "deleted node {}".format(node_index)
    return redirect(url_for('index'))
