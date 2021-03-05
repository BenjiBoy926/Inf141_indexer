class Posting:
    def __init__(self, document, score):
        self.document = document
        self.score = score

    def __str__(self):
        return f"Posting({self.document}, {self.score})"

    def __repr__(self):
        return f"Posting({self.document}, {self.score})"

    @staticmethod
    def merge(post1, post2):
        if post1.document == post2.document:
            return Posting(post1.document, post1.score + post2.score)
        else:
            raise TypeError(f"Cannot merge postings with different documents! "
                            f"Post 1: {post1.document}, Post 2: {post2.document}")
