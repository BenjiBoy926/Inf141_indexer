from bs4 import BeautifulSoup
from Inf141_tokenizer import PartA as tk
from stopwatch.stopwatch import Stopwatch
from posting import Posting
from pathlib import Path
import json


# Returns a tuple where the first item is the number of documents loaded
# and the second item is the index of all the documents
def indexJsonsInDirectory(directory, max_docs):
    index_file = open("index.txt", "w")
    total_docs = 0

    total_read_time = 0
    total_index_time = 0
    total_write_time = 0

    watch = Stopwatch()

    # Iterate over all folders in the dev path
    for path in Path(directory).iterdir():
        # Iterate over all json files in the current folder
        for json_file in Path(path).iterdir():
            try:
                print(f"Processing file {json_file}")

                # Open the file and load it as a json
                watch.restart()
                file = open(json_file, "r")
                json_data = json.load(file)
                file.close()
                total_read_time += watch.read()

                # Index the current json
                watch.restart()
                index = indexJson(json_data)
                total_index_time += watch.read()

                # Write the index to the file
                watch.restart()
                writeIndexToFile(index, index_file)
                total_write_time += watch.read()

                # Increment documents loaded
                total_docs += 1

                if total_docs >= max_docs:
                    break
            except Exception:
                index_file.close()
                raise

            if total_docs >= max_docs:
                break

    index_file.close()

    stat_file = open("report.txt", "w")
    stat_file.write(f"Average file read time:  {total_read_time / total_docs} \n")
    stat_file.write(f"Average indexing time:   {total_index_time / total_docs} \n")
    stat_file.write(f"Average file write time: {total_write_time / total_docs} \n")
    stat_file.close()


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
    indexJsonsInDirectory("developer/DEV", 2)
