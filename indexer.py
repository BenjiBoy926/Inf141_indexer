from bs4 import BeautifulSoup
from Inf141_tokenizer import PartA as tk
from stopwatch.stopwatch import Stopwatch
from posting import Posting
from pathlib import Path
import json
import os

# Returns a tuple where the first item is the number of documents loaded
# and the second item is the index of all the documents
def indexJsonsInDirectory(directory, max_docs):
    index_file = open("index.txt", "w")
    # total_index = {}
    total_docs = 0

    total_read_time = 0
    total_index_time = 0
    total_write_time = 0

    watch = Stopwatch()

    tokens_discovered = set()

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

                # TODO: merge the indices and detect how large the index is
                #  Once we are taking up 50% of RAM, dump the index into a file

                # Index the current json
                watch.restart()
                index = indexJson(json_data)
                # total_index = mergeIndices(total_index, index)
                total_index_time += watch.read()

                # Write the index to the file
                watch.restart()
                index = sorted(index.items())
                writeIndexToFile(index, index_file)
                total_write_time += watch.read()

                # Discover new tokens from the tokens in the index
                for token in index:
                    if token not in tokens_discovered:
                        tokens_discovered.add(token)

                # Increment documents loaded
                total_docs += 1

                if total_docs >= max_docs:
                    break
            except Exception:
                index_file.close()
                raise

        if total_docs >= max_docs:
            break

    stat_file = open("report.txt", "w")
    stat_file.write(f"Average file read time:  {total_read_time / total_docs} \n")
    stat_file.write(f"Average indexing time:   {total_index_time / total_docs} \n")
    stat_file.write(f"Average file write time: {total_write_time / total_docs} \n")
    stat_file.write(f"Total documents:         {total_docs} \n")
    stat_file.write(f"Total tokens:            {len(tokens_discovered)} \n")
    stat_file.write(f"Index size:              {os.path.getsize('index.txt')} KB \n")
    stat_file.close()

# Write the index to the given file
def writeIndexToFile(index, index_file):
    for token, postings in index:
        string = f"{token}"

        # Sort postings by document
        postings = sorted(postings, key=lambda p: p.document)

        for post in postings:
            string += f" {post.document} {post.score}"

        index_file.write(string)
        index_file.write("\n")

# Open all files in the directory as index files, merge them, and output them to the fout directory
def mergeIndicesInDirectory(directory, fout):
    files = []

    # Open all index files in the director
    for index_file in Path(directory).iterdir():
        files.append(open(index_file, "f"))

    # TODO: Merge the indices in the files

    # Close all of the files
    for index_file in files:
        index_file.close()


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
    indexJsonsInDirectory("developer/DEV", 200)
