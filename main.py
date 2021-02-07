from bs4 import BeautifulSoup
from Inf141_tokenizer import PartA as tk
from posting import Posting
from pathlib import Path
import json
import sys


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
            current_index = indexJson(json_data)
            index = mergeIndices(index, current_index)

            # Increment number of documents
            num_docs += 1

    return num_docs, index


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
    indices = {}

    # Build the soup of the current html file
    soup = BeautifulSoup(content, "html.parser")

    # Tokenize the html and compute frequencies of the tokens
    words = tk.tokenize(soup.get_text())
    frequencies = tk.computeWordFrequencies(words)

    for token, frequency in frequencies.items():
        if token in indices:
            indices[token].append(Posting(url, frequency))
        else:
            indices[token] = [Posting(url, frequency)]

    return indices


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data = indexJsonsInDirectory("developer/DEV")

    f = open("report.txt", "w")
    f.write(f"Number of documents: {data[0]} \n")
    f.write(f"Number of tokens:    {len(data[1])} \n")
    f.write(f"Index storage size:  {sys.getsizeof(data[1]) / 100}KB \n")
    f.close()
