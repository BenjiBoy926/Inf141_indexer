from posting import Posting

def serializeIndexItem(token, postings):
    # Sort postings by document
    postings = sorted(postings, key=lambda p: p.document)

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

def deserializeIndexItem(line):
    line = line.split(" ")
    postings = []

    for i in range(2, len(line)):
        if i % 2 == 0:
            postings.append(Posting(line[i], int(line[i + 1])))

    return line[0], int(line[1]), postings
