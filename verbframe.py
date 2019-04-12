import db

class Verbframe():
    #need to check for annotator later
    def __init__(self, word):
        verbs = db.get_db().execute(
            'SELECT id, sense_id, sense, args FROM verbs WHERE verb = ?',
            (word,)
        ).fetchall()
        self.verbs = []
        for verb in verbs:
            self.verbs.append({"id": verb[0], "sense_id": verb[1], "sense": verb[2], "args": verb[3]})
        self.num_senses = len(self.verbs)
        self.assigned_sense = None
