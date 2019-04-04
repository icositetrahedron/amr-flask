class NaiveBayes():

    def __init__(self):
        self.class_dict = {0: 'neg', 1: 'pos'}
        self.feature_dict = {0: 'great', 1: 'poor', 2: 'long'}
        self.docs_per_class = defaultdict(int)
        self.prior = np.zeros(len(self.class_dict))
        self.likelihood = np.zeros((len(self.class_dict), len(self.feature_dict)))
        #for information gain
        self.total_docs = 0
        self.docs_per_word = defaultdict(int)
        self.docs_per_class_per_word = defaultdict(lambda: defaultdict(int))

    def p_class_given_word(self, cls, word, reverse=False):
        docs_in_class_with_word = self.docs_per_class_per_word[word][cls]
        docs_with_word = self.docs_per_word[word]
        #find probability of class given word is NOT present
        if reverse:
            docs_in_class_with_word = self.docs_per_class[cls] - docs_in_class_with_word
            docs_with_word = self.total_docs - docs_with_word
        return docs_in_class_with_word / docs_with_word
