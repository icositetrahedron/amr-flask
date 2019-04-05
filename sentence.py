import db
from node import Node

class Sentence():
    #need to check for annotator later
    def __init__(self, id):
        sentence = db.get_db().execute(
            'SELECT sentence FROM raw_sentences WHERE id = ?',
            (id,)
        ).fetchone()
        self.id = id
        self.words = sentence[0].split()
        self.nodes = dict(map(self.row_to_node_tuple, db.get_db().execute(
            'SELECT word, word_index, sense, depth FROM annotated_nodes WHERE sentence_id = ?',
            (id,)
        ).fetchall()))
        self.relations = db.get_db().execute(
            'SELECT id, predicate, predicate_index, argument, argument_index, relation, relation_word_index, depth FROM annotated_relations WHERE sentence_id = ?',
            (id,)
        ).fetchall()

    def parse_command(self, command):
        components = command.split()

        predicate_index = components[0]
        if predicate_index == "root":
            predicate_index = 0
            predicate = "root"
            depth = 0
        else:
            predicate_index = int(predicate_index.strip("x"))
            predicate = self.words[predicate_index]
            depth = self.nodes[predicate_index].depth + 1

        relation = components[1]

        argument_index = int(components[2].strip("x"))
        argument = self.words[argument_index]

        self.nodes[argument_index] = Node(argument, argument_index, None, depth)

    def update_last_seen_time(self):
        db.get_db().execute(
            'UPDATE raw_sentences SET last_seen = CURRENT_TIMESTAMP WHERE id = ?',
            (self.id,)
        )

    def update_db(self):
        pass

    def row_to_node_tuple(self, row):
        return (row[1], Node(row[0], row[1], row[2], row[3]))
