class Posting:
    def __init__(self, document, score):
        self.document = document
        self.score = score

    def __str__(self):
        return f"Posting({self.document}, {self.score})"

    def __repr__(self):
        return f"Posting({self.document}, {self.score})"
