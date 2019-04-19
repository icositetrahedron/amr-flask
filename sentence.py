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
        self.annotated_indices = set([])
        self.root = None
        self.highlighted_node_index = None
        self.highlighted_node = None
        self.in_sense_editing_mode = False


    #e.g. root :top x18(say)
    #     x18 :arg0 x17
    def parse_command(self, command):
        components = command.split()

        #first argument in command
        #corresponds with parent node
        predicate = components[0]
        if predicate == "root":
            self.root = Node("root", 0, None, "top", 0, False)
            stem = self.root
        else:
            predicate_index = int(predicate.strip("x"))
            predicate = self.words[predicate_index-1]
            stem = self.root.get_node(predicate_index)

        #third argument in command
        #corresponds with child node
        argument_components = components[2].split("(")
        argument_index = int(argument_components[0].strip("x"))
        try:
            argument = argument_components[1].strip(")")
            manual_word = True
        except:
            argument = self.words[argument_index-1]
            manual_word = False

        #second argument in command
        #represents relationship between child and parent node
        relation = components[1]

        #adds argument as child of predicate in tree
        new_node = Node(argument, argument_index, None, relation, stem.depth + 1, manual_word)
        stem.add_child(new_node)
        self.annotated_indices.add(argument_index)

        if manual_word:
            self.highlighted_node = new_node
            self.highlighted_node_index = self.nodes_as_list().index(new_node)
            self.in_sense_editing_mode = True

    def set_verb_sense(self, sense):
        self.highlighted_node.set_sense(sense)

    def highlight_node_at_index(self, node_index, edit):
        self.highlighted_node_index = node_index
        self.highlighted_node = self.nodes_as_list()[node_index]
        self.in_sense_editing_mode = edit

    #deletes node (corresponds with annotated word in sentence) from tree
    def delete_node(self, node_index):
        self.annotated_indices = set([])
        if node_index == 0:
            self.root = None
        else:
            self.root.delete_child(self.nodes_as_list()[node_index].word_index)
            for child in self.nodes_as_list():
                self.annotated_indices.add(child.word_index)
        self.highlighted_node = None

    #returns shallow list of children (see Node.flattened_children)
    def nodes_as_list(self):
        if self.root is not None:
            return self.root.flattened_tree()
        return []

    #updates database so sentence will be reopened on load
    def update_last_seen_time(self):
        db.get_db().execute(
            'UPDATE raw_sentences SET last_seen = CURRENT_TIMESTAMP WHERE id = ?',
            (self.id,)
        )

    def update_db(self):
        pass
