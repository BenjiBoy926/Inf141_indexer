from bs4 import BeautifulSoup
from Inf141_tokenizer import PartA as tk
from posting import Posting
from pathlib2 import Path
import json
import os
from collections import defaultdict
import serializer as sz

# TODO: store term and collection statistics at the top of the index (lecture 18)?
# TODO: split inverted index into alphabet ranges (lecture 18)?
# Returns a tuple where the first item is the number of documents loaded
# and the second item is the index of all the documents
def indexJsonsInDirectory(directory, max_docs, batch_size):
    cleanupOldIndices()

    total_index = {}

    total_docs = 0
    current_index = 0

    # Iterate over all folders in the dev path
    for path in Path(directory).iterdir():
        # Iterate over all json files in the current folder
        for json_file in Path(path).iterdir():
            print(f"Processing file {json_file}")

            # Open the file and load it as a json
            file = open(json_file, "r")
            json_data = json.load(file)
            file.close()

            # Submit request to url
            # If OK, index the document

            # Index the current json and merge it with the overall json
            index = indexJson(json_data)
            total_index = mergeIndices(total_index, index)

            # Increment documents loaded
            total_docs += 1

            # If we have read in the batch size, offload the index
            if total_docs % batch_size == 0:
                writeIndexToFileDirectory(total_index, f"indices/index{current_index}.txt")
                total_index = {}
                current_index += 1

            if total_docs >= max_docs > 0:
                break

        if total_docs >= max_docs > 0:
            break

    # If there is some index left over at the end, write it out to the current index
    if len(total_index) > 0:
        writeIndexToFileDirectory(total_index, f"indices/index{current_index}.txt")

    print("Merging indices...")
    mergeIndicesInDirectory("indices", "index.txt")


# Open the file at the directory and write the index into it
def writeIndexToFileDirectory(index, index_dir):
    print(f"Writing current index to file {index_dir}")
    index_file = open(index_dir, "w")
    writeIndexToFile(index, index_file)
    index_file.close()

def cleanupOldIndices():
    for path in Path("indices").iterdir():
        os.remove(path)

    removeIfExists("index.txt")
    removeIfExists("index.txt.0")
    removeIfExists("index.txt.1")

def removeIfExists(directory):
    if os.path.exists(directory):
        os.remove(directory)

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
            iindex = f"{fout}.{i % 2}"
            oindex = f"{fout}.{(i + 1) % 2}"

            print(f"Merging {iindex} and partial_index{i}.txt to {oindex}")
            outFile = open(f"{iindex}", "r")
            mergeTwoIndexFiles(outFile, files[i], f"{oindex}")
            outFile.close()

        # Rename the last file written to index.txt
        os.rename(f"{fout}.{len(files) % 2}", fout)

    # Close all of the files
    for index_file in files:
        index_file.close()

def mergeTwoIndexFiles(index1, index2, fout):
    fout = open(fout, "w")

    # Read the first lines in the index files
    line1 = index1.readline()
    line2 = index2.readline()

    # Loop until the end of either file
    while line1 != "" and line2 != "":
        # Read through the first file until a token is found that comes lexically after
        # the current token in the second file
        line2Data = line2.split(" ")
        line1 = lexicalFileReader(index1, fout, line1, line2Data[0])

        # Now read through the SECOND file until a token is found that comes lexically after
        # the current token in the FIRST file
        line1Data = line1.split(" ")
        line2 = lexicalFileReader(index2, fout, line2, line1Data[0])

        # If the entries are equal, we need to merge them
        if line1Data[0] == line2Data[0]:
            # Create a single-entry index with all postings from both files
            index = {}
            item1 = sz.deserializeIndexItem(line1)
            item2 = sz.deserializeIndexItem(line2)
            item1[2].extend(item2[2])
            index[item1[0]] = item1[2]

            # Write the single-entry index to the file. This sorts the posting lists for us
            writeIndexToFile(index, fout)

            # Update to the next line
            line1 = index1.readline()
            line2 = index2.readline()

    # Read the rest of the longer file
    if line1 != "":
        longer_index = index1
    else:
        longer_index = index2

    line1 = longer_index.readline()

    while line1 != "":
        # Write the same line out the file
        fout.write(line1)

        # Read the next line in the longer index
        line1 = longer_index.readline()

    fout.close()

# Output each file in the in_file until a line is found in the in_file
# that comes lexically after the sentinel value given
# Return the last line read
def lexicalFileReader(in_file, out_file, first_line, sentinel):
    line = first_line
    data = line.split(" ")

    while line != "" and data[0] < sentinel:
        out_file.write(line)
        line = in_file.readline()
        if line != "":
            data = line.split(" ")

    return line

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


def validateIndexFile(index):
    tokens = set()
    index = open(index, "r")

    for line in index:
        lineData = line.split(" ")

        if lineData[0] not in tokens:
            tokens.add(lineData[0])
        else:
            index.close()
            return False

    index.close()
    return True


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    indexJsonsInDirectory("developer/DEV", -1, 2000)

    if validateIndexFile("index.txt"):
        print("Index is valid!")
    else:
        print("Index is NOT VALID!")
