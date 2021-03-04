# TODO: an optimization - use "skip pointers" in the index searched

from Inf141_tokenizer import PartA as tk
from collections import defaultdict
from stopwatch.stopwatch import Stopwatch
from lexicon import readLexicon
import serializer as sz
from posting import Posting


# TODO: multithreading to search indices in different lexical ranges at the same time?
# Returns a list of postings where all terms appeared
# The score of each positing is the sum of the scores of the postings for each term
def searchQuery(query, index, lex):
    query = tk.tokenize(query)
    results = dict()

    for token in query:
        # (token, doc_freq, posting_list)
        indexItem = searchToken(token, index, lex)
        # token --> posting_list
        results[indexItem[0]] = indexItem[2]

    # Return only urls of sites that have ALL the query words
    # At this point, results changes from a dictionary mapping the token-posting_list pairs to only a list of postings
    if len(query) > 1:
        # [posting_list, posting_list, ... ]
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
        line = index.readline()
        return sz.deserializeIndexItem(line)
    else:
        return token, 0, []


# Merge two posting lists together and sort them least to greatest
def mergeTwoPostingLists(list1, list2):
    ret = []
    i = 0

    # Make sure list1 has the smaller list
    if len(list1) > len(list2):
        temp = list1
        list1 = list2
        list2 = temp

    # Loop through the postings in the first list
    for post in list1:
        # Loop through the second list until a posting is found that is greater than or equal to the current post
        while list2[i].document < post.document:
            i += 1

        # If the two documents are equal, add it to the return list
        if post.document == list2[i].document:
            ret.append(Posting.merge(post, list2[i]))
            i += 1

    return sorted(ret, key=lambda p: p.document)


def mergePostingLists(postingLists):
    # Sort the postings lists smallest to largest
    postingLists = sorted(postingLists, key=lambda l: len(l))

    # Merge the first two postings lists
    ret = mergeTwoPostingLists(postingLists[0], postingLists[1])

    if len(postingLists) > 2:
        for postingList in postingLists[2:]:
            ret = mergeTwoPostingLists(ret, postingList)

    return ret


def resultString(query, results, t):
    string = f"Results for query: '{query}'\n"
    string += f"Completed in {t} secs\n"
    string += f"Total results: {len(results)}\n"

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

    print("Getting lexicon for faster searching...")
    watch.restart()
    theLex = readLexicon("lexicon.txt")
    print(f"Finished reading lexicon in {watch.read()} secs")

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
