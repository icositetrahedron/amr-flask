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

def save_current_sentence_in_db():
    get_current_sentence().update_db()

def display():
    sentence = get_current_sentence()
    print("sense editing mode:", sentence.in_sense_editing_mode)
    print("higlighted node:", sentence.highlighted_node_index)
    nodes = sentence.nodes_as_list()
    num_words = len(sentence.words)
    node_indices = range(len(nodes))
    return render_template('annotater.html',
                           sentence=sentence,
                           indices=range(num_words),
                           nodes=nodes,
                           node_indices=node_indices,
                           total_sentences=len(get_sentences()))

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        if "set_sentence" in request.form:
            print("setting sentence")
            save_current_sentence_in_db()
            set_current_sentence_id(request.form["sentence_id"])
        elif "add_relation" in request.form:
            #e.g. root :top x18(say)
            #     x18 :arg0 x17
            print("adding relation")
            parse_command(request.form["relation"])
        elif "set_sense" in request.form:
            print("setting sense")
            set_verb_sense(request.form["sense_selection"])
        else:
            print(request.form)
    return display()

def parse_command(raw_command):
    sentences = get_sentences()
    sentences[get_current_sentence_id()-1].parse_command(raw_command)
    set_sentences(sentences)
    g.last_command = raw_command

def set_verb_sense(sense):
    sense = int(sense)
    sentences = get_sentences()
    sentence = sentences[get_current_sentence_id()-1]
    sentence.set_verb_sense(sense)
    g.last_command = "set sense of {} to {}".format(sentence.highlighted_node.word, sense)
    sentence.in_sense_editing_mode = False
    set_sentences(sentences)
    print("sense set")

@app.route('/delete_node/<node_index>', methods=['GET', 'POST'])
def delete_node(node_index):
    node_index = int(node_index)
    sentences = get_sentences()
    sentence = sentences[get_current_sentence_id()-1]
    sentence.delete_node(node_index)
    set_sentences(sentences)
    g.last_command = "deleted node {}".format(node_index)
    return redirect(url_for('index'))

@app.route('/edit_sense/<node_index>', methods=['GET', 'POST'])
def edit_sense(node_index):
    node_index = int(node_index)
    sentences = get_sentences()
    sentence = sentences[get_current_sentence_id()-1]
    sentence.highlight_node_at_index(node_index, True)
    set_sentences(sentences)
    return redirect(url_for('index'))
