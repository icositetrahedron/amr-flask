import os, pickle
from flask import Flask, render_template, request, g, redirect, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
import db, cmd
from sentence import Sentence
from user import RegistrationForm, User

app = Flask(__name__)
app.config.from_envvar('AMR_SETTINGS', silent=True)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


def set_user(user):
    try:
        users = pickle.load(open("users.pickle","rb"))
    except:
        users = {}
    users_pickle = open("users.pickle","wb")
    users[user.get_id()] = user
    pickle.dump(users, users_pickle)
    users_pickle.close()

def get_user(id):
    return pickle.load(open("users.pickle","rb"))[str(id)]

def set_sentences(sentences):
    users = pickle.load(open("sentences.pickle","rb"))
    users[current_user.get_id()] = sentences
    sentences_pickle = open("sentences.pickle","wb")
    pickle.dump(users, sentences_pickle)
    sentences_pickle.close()

def get_sentences():
    print("CURRENT USER:", current_user.username, current_user.get_id())
    try:
        users = pickle.load(open("sentences.pickle","rb"))
    except:
        users = {}
    if current_user.get_id() in users:
        return users[current_user.get_id()]
    else:
        print(users)
        max_sentence = db.get_db().execute(
            'SELECT MAX(id) FROM raw_sentences'
        ).fetchone()
        if max_sentence is not None:
            total_sentences = max_sentence[0]
        sentences = list(map(lambda id: Sentence(id), range(1, total_sentences+1)))
        users[current_user.get_id()] = sentences
        sentences_pickle = open("sentences.pickle","wb")
        pickle.dump(users, sentences_pickle)
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
@login_required
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
    g.last_command = "set sense of <i>{}</i> to {}".format(sentence.highlighted_node.word, sense)
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

@app.route('/view_senses/<node_index>', methods=['GET', 'POST'])
def view_senses(node_index):
    node_index = int(node_index)
    sentences = get_sentences()
    sentence = sentences[get_current_sentence_id()-1]
    sentence.highlight_node_at_index(node_index, False)
    set_sentences(sentences)
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print(db.get_db().execute('SELECT * FROM users').fetchall())
        user_id = db.get_db().execute(
            'SELECT id FROM users WHERE username = ? AND password = ?',
            (request.form['username'],request.form['password'])
        ).fetchone()
        if user_id is None:
            error = 'Invalid username/password'
        else:
            login_user(get_user(user_id[0]))
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('show_entries'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        db.get_db().execute(
            'INSERT INTO users (username, password, email) VALUES (?,?,?);',
            (form.username.data,form.password.data,form.email.data)
        )
        db.get_db().commit()
        new_id = db.get_db().execute('SELECT id FROM users WHERE username = ?', (form.username.data,)).fetchone()[0]
        user = User(id=new_id, username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        set_user(user)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
