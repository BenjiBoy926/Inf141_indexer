from bs4 import BeautifulSoup
from Inf141_tokenizer import PartA as tk
from posting import Posting
from pathlib import Path
import json
import sys
import os


# Returns a tuple where the first item is the number of documents loaded
# and the second item is the index of all the documents
def indexJsonsInDirectory(directory):
    num_docs = 0
    unique_terms = 0
    discovered_tokens = []
    index_file = open("index.txt", "w")

    # Iterate over all folders in the dev path
    for path in Path(directory).iterdir():
        # Iterate over all json files in the current folder
        for json_file in Path(path).iterdir():
            try:
                print(f"Loading file {json_file}")

                # Open the file and load it as a json
                file = open(json_file, "r")
                json_data = json.load(file)
                file.close()

                print(f"Indexing file {json_file}")

                # Index the current json
                index = indexJson(json_data)

                print(f"Storing index for file {json_file}")

                # Write the index to the file
                writeIndexToFile(index, index_file)

                print(f"Searching for new terms discovered")

                # Check for new tokens that have been discovered and increment the number found
                for token in index:
                    if token not in discovered_tokens:
                        discovered_tokens.append(token)
                        unique_terms += 1

                # Increment number of documents
                num_docs += 1
            except Exception:
                index_file.close()
                raise

    index_file.close()
    return num_docs, unique_terms


def writeIndexToFile(index, index_file):
    for token, postings in index.items():
        for post in postings:
            index_file.write(f"{token} {post.document} {post.score} \n")

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
    f.write(f"Number of tokens:    {data[1]} \n")
    f.write(f"Index storage size:  {os.path.getsize('index.txt') / 100} KB \n")
    f.close()
