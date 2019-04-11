class Node():

    def __init__(self, word, word_index, sense):
        self.word = word
        self.word_index = word_index
        self.sense = sense
        self.children = []

    def add_child(self, child, relation):
        self.children.append((child, relation))

    def get_node(self, word_index):
        for (child, relation) in self.children:
            if child.word_index == word_index:
                return child
            descendant = child.get_node(word_index)
            if descendant is not None:
                return descendant
        return None

    def delete_node(self, word_index):
        for i in range(len(self.children)):
            child = self.children[i][0]
            if child.word_index == word_index:
                self.children.pop(i)
                return
            else:
                child.delete_node(word_index)

    #returns list of children, where
    # each child is a dictionary containing attributes of that child
    def flattened_children(self, depth):
        children = []
        for (child, relation) in self.children:
            child_values = dict()
            child_values["word"] = child.word
            child_values["word_index"] = child.word_index
            child_values["sense"] = child.sense
            child_values["relation"] = relation
            child_values["depth"] = depth+1
            children.append(child_values)
            children += child.flattened_children(depth+1)
        return children
