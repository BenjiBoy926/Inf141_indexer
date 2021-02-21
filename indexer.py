from bs4 import BeautifulSoup
from Inf141_tokenizer import PartA as tk
from stopwatch.stopwatch import Stopwatch
from posting import Posting
from pathlib import Path
import json
import os
import sys
from collections import defaultdict
import psutil

# TODO: store term and collection statistics at the top of the index (lecture 18)?
# TODO: split inverted index into alphabet ranges (lecture 18)?
# Returns a tuple where the first item is the number of documents loaded
# and the second item is the index of all the documents
def indexJsonsInDirectory(directory, max_docs):
    index_file = open("index.txt", "w")
    total_index = {}

    total_docs = 0
    current_index = 0

    # Store half the available memory at the start of the indexing
    halfmem = psutil.virtual_memory().available / 2

    # Iterate over all folders in the dev path
    for path in Path(directory).iterdir():
        # Iterate over all json files in the current folder
        for json_file in Path(path).iterdir():
            try:
                print(f"Processing file {json_file}")

                # Open the file and load it as a json
                file = open(json_file, "r")
                json_data = json.load(file)
                file.close()

                # Index the current json and merge it with the overall json
                index = indexJson(json_data)
                total_index = mergeIndices(total_index, index)

                # Check if the size of the total index has grown beyond half the available RAM
                if sys.getsizeof(total_index) >= halfmem:
                    print("Dumping current index to file")
                    total_index = sorted(total_index.items())
                    writeIndexToFile(total_index, f"indices/index{current_index}.txt")
                    total_index = {}
                    current_index += 1

                # Increment documents loaded
                total_docs += 1

                if total_docs >= max_docs > 0:
                    break
            except Exception:
                index_file.close()
                raise

        if total_docs >= max_docs > 0:
            break

    total_index = sorted(total_index.items())
    writeIndexToFile(total_index, f"indices/index{current_index}.txt")
    mergeIndicesInDirectory("indices", "index.txt")


# Write the index to the given file
def writeIndexToFile(index, index_file):
    index_file = open(index_file, "w")

    for token, postings in index:
        # Sort postings by document
        postings = sorted(postings, key=lambda p: p.document)

        string = f"{token} {len(postings)}"

        for post in postings:
            string += f" {post.document} {post.score}"

        index_file.write(string)
        index_file.write("\n")

    index_file.close()

# Open all files in the directory as index files, merge them, and output them to the fout directory
def mergeIndicesInDirectory(directory, fout):
    files = []

    # Open all index files in the directory
    for index_file in Path(directory).iterdir():
        files.append(open(index_file, "f"))

    # TODO: Merge the indices in the files

    # Close all of the files
    for index_file in files:
        index_file.close()

def mergeTwoIndexFiles(index1, index2, fout):
    line1 = index1.readline().split(" ")
    line2 = index2.readline().split(" ")

    


# Merge two indices by adding the postings from index2 to the list of postings in index1
def mergeIndices(index1, index2):
    new_index = index1

    for token, frequency in index2.items():
        # If this token in index2 already appears in index1,
        # add all postings from the token in index2 to the token in index1
        if token in new_index:
            new_index[token].extend(index2[token])
        # If this token in index2 is not yet in index1,
        # add it to the dictionary
        else:
            new_index[token] = index2[token]

    return new_index


def indexJson(j):
    return indexDocument(j['url'], j['content'])


def indexDocument(url, content):
    indices = defaultdict(lambda: [])

    # Build the soup of the current html file
    soup = BeautifulSoup(content, "html.parser")

    # Tokenize the html and compute frequencies of the tokens
    words = tk.tokenize(soup.get_text())
    frequencies = tk.computeWordFrequencies(words)

    for token, frequency in frequencies.items():
        # TODO: add the token positions when we add the posting? (better for ranking)
        indices[token].append(Posting(url, frequency))

    return indices


# Create an index of the index.
# The index of the index maps the term to the character position in the file
def lexicon(index):
    lex = {}
    index = open(index, "r")
    line = "nonempty"

    # Read the file until you read an empty line
    while line != "":
        pos = index.tell()
        line = index.readline()
        lineData = line.split(" ")
        lex[lineData[0]] = pos

    index.close()
    return lex


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    indexJsonsInDirectory("developer/DEV", 200)
