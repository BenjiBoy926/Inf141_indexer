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


def writeLexicon(lex, lex_file):
    lex_file = open(lex_file, "w")

    for token, pos in lex.items():
        lex_file.write(token)
        lex_file.write(" ")
        lex_file.write(str(pos))
        lex_file.write("\n")

    lex_file.close()


def readLexicon(lex_file):
    lex = {}
    lex_file = open(lex_file, "r")

    for line in lex_file:
        lineData = line.split(" ")
        lex[lineData[0]] = int(lineData[1])

    lex_file.close()
    return lex


if __name__ == "__main__":
    print("Building lexicon...")
    theLex = lexicon("index.txt")
    print("Writing lexicon to file...")
    writeLexicon(theLex, "lexicon.txt")
