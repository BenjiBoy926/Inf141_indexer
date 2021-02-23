from bs4 import BeautifulSoup
from Inf141_tokenizer import PartA as tk
from stopwatch.stopwatch import Stopwatch
from posting import Posting
from pathlib2 import Path
import json
import os
import sys
from collections import defaultdict
import psutil
import serializer as sz

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
                    writeIndexToFileDirectory(total_index, f"indices/index{current_index}.txt")
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

    writeIndexToFileDirectory(total_index, f"indices/index{current_index}.txt")

    print("Merging indices...")
    mergeIndicesInDirectory("indices", "index.txt")


# Open the file at the directory and write the index into it
def writeIndexToFileDirectory(index, index_dir):
    print(f"Writing current index to file {index_dir}")
    index_file = open(index_dir, "w")
    writeIndexToFile(index, index_file)
    index_file.close()

# Write the index to the given file
# The index file object passed to the function needs to already be open
def writeIndexToFile(index, index_file):
    index = sorted(index.items())

    for token, postings in index:
        index_file.write(sz.serializeIndexItem(token, postings))
        index_file.write("\n")

# Open all files in the directory as index files, merge them, and output them to the fout directory
def mergeIndicesInDirectory(directory, fout):
    files = []

    # Open all index files in the directory
    for index_file in Path(directory).iterdir():
        files.append(open(index_file, "r"))

    # If there is only one file, output it to the given directory
    if len(files) == 1:
        print("Writing single index to output directory")
        fout = open(fout, "w")
        for line in files[0]:
            fout.write(line)
        fout.close()

    # If there are two files, merge them and output them to the directory
    elif len(files) == 2:
        print("Merging two indices into output directory")
        mergeTwoIndexFiles(files[0], files[1], fout)

    # If there are many files, merge them all
    else:
        print(f"Merging partial_index0.txt and partial_index1.txt to {fout}.0")
        mergeTwoIndexFiles(files[0], files[1], f"{fout}.0")

        # Merge the first two, then merge THAT result with each other file
        for i in range(2, len(files)):
            print(f"Merging {fout}.{i % 2} and partial_index{i}.txt to {fout}.{(i + 1) % 2}")
            outFile = open(f"{fout}.{i % 2}", "w")
            mergeTwoIndexFiles(outFile, files[i], f"{fout}.{(i + 1) % 2}")
            outFile.close()

    # TODO: rename the last file output to to {fout}

    # Close all of the files
    for index_file in files:
        index_file.close()

def mergeTwoIndexFiles(index1, index2, fout):
    fout = open(fout, "w")

    # Read the first lines in the index files
    line1 = index1.readline()
    line2 = index2.readline()

    # Store half the available memory at the start of the indexing
    halfmem = psutil.virtual_memory().available / 2

    # Index stored in RAM
    index = {}

    # Loop until the end of either file
    while line1 != "" and line2 != "":
        # Deserialize the current index items
        line1 = sz.deserializeIndexItem(line1.split(" "))
        line2 = sz.deserializeIndexItem(line2.split(" "))

        # If the two words are equal, then add the word to the index with the postings lists merged
        if line1[0] == line2[0]:
            index[line1[0]] = line1[2].extend(line2[2])
        # If the terms are unequal, add them to the index separately
        else:
            index[line1[0]] = line1[2]
            index[line2[0]] = line2[2]

        # If the index in RAM exceeds half available memory, dump it to the file
        if sys.getsizeof(index) >= halfmem:
            writeIndexToFile(index, fout)
            index = {}

        # Read the next lines in the files
        line1 = index1.readline()
        line2 = index2.readline()

    # Read the rest of the longer file
    if line1 != "":
        longer_index = index1
    else:
        longer_index = index2

    line1 = longer_index.readline()

    while line1 != "":
        # Deserialize the current index items
        line1 = sz.deserializeIndexItem(line1.split(" "))
        index[line1[0]] = line1[2]

        # If the index in RAM exceeds half available memory, dump it to the file
        if sys.getsizeof(index) >= halfmem:
            writeIndexToFile(index, fout)
            index = {}

        # Read the next line in the longer index
        line1 = longer_index.readline()

    fout.close()


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
# The index of the index (lexicon) maps the term to the character position in the file
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
    indexJsonsInDirectory("developer/DEV", 1000)
