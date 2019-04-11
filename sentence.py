import db
from node import Node

class Sentence():
    #need to check for annotator later
    def __init__(self, id):
        print("making sentence for ID: ", id)
        sentence = db.get_db().execute(
            'SELECT sentence FROM raw_sentences WHERE id = ?',
            (id,)
        ).fetchone()
        self.id = id
        self.words = sentence[0].split()
        self.annotated_indices = set([])
        self.root = None

    def parse_command(self, command):
        components = command.split()

        predicate = components[0]
        if predicate == "root":
            self.root = Node("root", 0, None)
            stem = self.root
        else:
            predicate_index = int(predicate.strip("x"))
            predicate = self.words[predicate_index-1]
            stem = self.root.get_node(predicate_index)

        relation = components[1]


        argument_components = components[2].split("(")
        argument_index = int(argument_components[0].strip("x"))
        try:
            argument = argument_components[1].strip(")")
        except:
            argument = self.words[argument_index-1]

        stem.add_child(Node(argument, argument_index, None), relation)
        self.annotated_indices.add(argument_index)

    def delete_node(self, node_index):
        self.annotated_indices = set([])
        if node_index == 0:
            self.root = None
        else:
            self.root.delete_node(self.nodes_as_list()[node_index]["word_index"])
            for (child, relation) in self.root.flattened_children(0):
                self.annotated_indices.append(child["word_index"])

    def nodes_as_list(self):
        if self.root is not None:
            root_dict = {"word": "root", "word_index": "", "sense": "", "relation": "top", "depth":0}
            return [root_dict] + self.root.flattened_children(0)
        return []

    def update_last_seen_time(self):
        db.get_db().execute(
            'UPDATE raw_sentences SET last_seen = CURRENT_TIMESTAMP WHERE id = ?',
            (self.id,)
        )

    def update_db(self):
        pass
