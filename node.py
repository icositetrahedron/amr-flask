from verbframe import Verbframe

class Node():

    def __init__(self, word, word_index, sense, relation_to_parent, manual_word):
        self.word = word
        self.word_index = word_index
        self.sense = sense
        self.relation_to_parent = relation_to_parent
        self.manual_word = manual_word
        self.children = []
        self.verbframe = None

        if manual_word:
            self.verbframe = Verbframe(word)

    def set_sense(self, sense):
        self.verbframe.assigned_sense = sense

    def add_child(self, child):
        self.children.append(child)

    def get_node(self, word_index):
        for child in self.children:
            if child.word_index == word_index:
                return child
            descendant = child.get_node(word_index)
            if descendant is not None:
                return descendant
        return None

    def delete_child(self, word_index):
        for i in range(len(self.children)):
            child = self.children[i]
            if child.word_index == word_index:
                self.children.pop(i)
                return
            else:
                child.delete_child(word_index)

    #returns list of nodes (self and children), where
    # each node is a dictionary containing attributes of that node
    def flattened_tree(self, depth):
        values = dict()
        values["word"] = self.word
        values["word_index"] = self.word_index
        values["sense"] = self.sense
        values["relation"] = self.relation_to_parent
        values["manual_word"] = self.manual_word
        values["verbframe"] = self.verbframe
        values["depth"] = depth+1
        nodes = [values]
        for child in self.children:
            nodes += child.flattened_tree(depth+1)
        return nodes
