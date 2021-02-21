# TODO: we need the Posting to have the docID as an integer,
#  otherwise we will never be able to get the required speed of 300 ms
class Posting:
    def __init__(self, document, score):
        self.document = document
        self.score = score
        # TODO: store the positions of the term in the document
        self.positions = []

    def __str__(self):
        return f"Posting({self.document}, {self.score}, {self.positions})"

    def __repr__(self):
        return f"Posting({self.document}, {self.score}, {self.positions})"
