# TODO: an optimization - use "skip pointers" in the index searched

from Inf141_tokenizer import PartA as tk
from collections import defaultdict
from stopwatch.stopwatch import Stopwatch
from indexer import lexicon

# TODO: multithreading to search indices in different lexical ranges at the same time?
def searchQuery(query, index, lex):
    query = tk.tokenize(query)
    results = dict()

    for token in query:
        results[token] = searchToken(token, index, lex)

    # Return only urls of sites that have ALL the query words
    if len(query) > 1:
        results = dictIntersect([dictionary for dictionary in results.values()])
    else:
        results = results[query[0]]

    return sorted(results.items(), key=lambda t: t[1], reverse=True)


def searchToken(token, index, lex):
    # Process in order of increasing frequency (why we need document frequency in the index)
    # AND, OR, NOT?
    urls = defaultdict(int)

    # Check if the token searched for is in the lexicon
    if token in lex:
        # Seek to the place in the file that the lexicon specifies
        index.seek(lex[token])

        # Read the line and split it on spaces
        line = index.readline().split(" ")

        # Loop from the first posting at index 2
        for i in range(2, len(line)):

            # Take all urls
            if i % 2 == 0:
                url = line[i]
                freq = int(line[i + 1])
                urls[url] += freq

    return urls


def dictIntersect(dictList):
    ret = {}

    for key in dictList[0]:
        results = [key in dictionary for dictionary in dictList[1:]]
        if all(results):
            ret[key] = sum([dictionary[key] for dictionary in dictList])

    return ret


def resultString(query, results, t):
    string = f"Results for query: '{query}'\n"
    string += f"Completed in {t} secs\n"

    size = min(5, len(results))

    if size > 0:
        string += f"Top results:\n"
        for i in range(size):
            string += f"{results[i][0]}\n"
    else:
        print("No results found\n")

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
