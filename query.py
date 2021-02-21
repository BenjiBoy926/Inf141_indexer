# TODO: an optimization - use "skip pointers" in the index searched

from Inf141_tokenizer import PartA as tk
from collections import defaultdict
from stopwatch.stopwatch import Stopwatch
from indexer import lexicon
import serializer as sz
from posting import Posting

# TODO: multithreading to search indices in different lexical ranges at the same time?
def searchQuery(query, index, lex):
    query = tk.tokenize(query)
    results = dict()

    for token in query:
        indexItem = searchToken(token, index, lex)
        results[indexItem[0]] = indexItem[2]

    # Return only urls of sites that have ALL the query words
    # At this point, results changes from a dictionary mapping the token-posting_list pairs to only a list of postings
    if len(query) > 1:
        results = [postings for postings in results.values()]
        results = mergePostingLists(results)
    else:
        results = results[query[0]]

    return sorted(results, key=lambda t: t.score, reverse=True)


def searchToken(token, index, lex):
    # Check if the token searched for is in the lexicon
    if token in lex:
        # Seek to the place in the file that the lexicon specifies
        index.seek(lex[token])

        # Read the line and split it on spaces
        line = index.readline().split(" ")
        return sz.deserializeIndexItem(line)
    else:
        return token, 0, []

def mergePostingLists(postingLists):
    ret = []

    # Loop through the postings in the first list
    for post in postingLists[0]:
        # Generate a list of true/false that are true if the positing is in the other list
        urls_in_others = [post.document == other.document for other in postingLists[1:]]

        # If the posting is in all other positing lists, add a new posting to the result
        if all(urls_in_others):
            score = sum([p.score for p in postingLists])
            ret.append(Posting(post.document, score))

    return ret


def resultString(query, results, t):
    string = f"Results for query: '{query}'\n"
    string += f"Completed in {t} secs\n"

    size = min(5, len(results))

    if size > 0:
        string += f"Top results:\n"
        for i in range(size):
            string += f"{results[i].document}\n"
    else:
        string += "No results found\n"

    return string


if __name__ == "__main__":
    print("Welcome to our searching engine!")

    userInput = "not x"
    fout = open("searchReport.txt", "w")
    indexFile = open("index.txt", "r")
    watch = Stopwatch()

    print("Building lexicon for faster searching...")
    theLex = lexicon("index.txt")

    while userInput != "x":
        userInput = input("Enter the terms to search for (type 'x' to exit): ")

        if userInput != "x":
            print("Searching...")
            watch.restart()
            output = searchQuery(userInput, indexFile, theLex)
            output = resultString(userInput, output, watch.read())

            print()
            print(output)
            print("Results output to file: searchReport.txt")
            print()

            fout.write(f"{output}\n")
        else:
            print("Thanks for using our search application!")
