from posting import Posting

def serializeIndexItem(token, postings):
    # Sort postings by document
    postings = sorted(postings, key=lambda p: p.score)

    string = f"{token} {len(postings)}"

    for post in postings:
        string += f" {post.document} {post.score}"

    return string

def serializeIndex(index):
    string = ""

    for token, postings in index:
        string += serializeIndexItem(token, postings)
        string += "\n"

    return string

def deserializeIndexItem(lineData):
    postings = []

    for i in range(2, len(lineData)):
        if i % 2 == 0:
            postings.append(Posting(lineData[i], lineData[i + 1]))

    return lineData[0], lineData[1], postings
