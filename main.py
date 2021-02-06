from bs4 import BeautifulSoup
from tokenizer import PartA as tk
from posting import Posting
from pathlib import Path
import json
import sys

# Get all folders in a given folder
# def getSubDirs(directory):
#     subdirs = []
#
#     for path in Path(directory).iterdir():
#         if path.is_dir():
#             subdirs.append(path)
#
#     return subdirs
#
# # Load all of the json files in the directory and return the list of jsons
# def loadJsonInDirectory(directory):
#     jsons = []
#
#     for path in Path(directory).iterdir():
#         # If this path is a directory, load all jsons in THAT directory, and add those jsons to this list
#         if path.is_file():
#             file = open(path, "r")
#             jsons.append(json.load(file))
#             file.close()
#
#     return jsons

# Returns a tuple where the first item is the number of documents loaded
# and the second item is the index of all the documents
def indexJsonsInDirectory(directory):
    index = {}
    num_docs = 0

    # Iterate over all folders in the dev path
    for path in Path(directory).iterdir():
        # Iterate over all json files in the current folder
        for json_file in Path(path).iterdir():
            print(f"Processing file {json_file}")

            # Open the file and load it as a json
            file = open(json_file, "r")
            json_data = json.load(file)
            file.close()

            # Index the current json and merge it with the overall index
            current_index = indexDocument(json_data)
            index = mergeIndices(index, current_index)

            # Increment number of documents
            num_docs += 1

    return num_docs, index


# Return a dictionary where the token is the key and the value is the token's list of postings
# def indexDocumentList(json_list):
#     indices = {}
#     for j in json_list:
#         # Build the soup of the current html file
#         soup = BeautifulSoup(j['content'], "html.parser")
#
#         # Tokenize the html and compute frequencies of the tokens
#         words = tk.tokenize(soup.get_text())
#         frequencies = tk.computeWordFrequencies(words)
#
#         for token, frequency in frequencies.items():
#             if token in indices:
#                 indices[token].append(Posting(j['url'], frequency))
#             else:
#                 indices[token] = [Posting(j['url'], frequency)]
#
#     return indices


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


def indexDocument(j):
    indices = {}

    # Build the soup of the current html file
    soup = BeautifulSoup(j['content'], "html.parser")

    # Tokenize the html and compute frequencies of the tokens
    words = tk.tokenize(soup.get_text())
    frequencies = tk.computeWordFrequencies(words)

    for token, frequency in frequencies.items():
        if token in indices:
            indices[token].append(Posting(j['url'], frequency))
        else:
            indices[token] = [Posting(j['url'], frequency)]

    return indices


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data = indexJsonsInDirectory("developer/DEV")

    f = open("report.txt", "w")
    f.write(f"Number of documents: {data[0]} \n")
    f.write(f"Number of tokens:    {len(data[1])} \n")
    f.write(f"Index storage size:  {sys.getsizeof(data[1]) / 100}KB \n")
    f.close()

    print("Finished writing report, exiting")
