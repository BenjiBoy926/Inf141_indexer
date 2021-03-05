# TODO: an optimization - use "skip pointers" in the index searched

from Inf141_tokenizer import PartA as tk
from stopwatch.stopwatch import Stopwatch
from lexicon import readLexicon
import serializer as sz
from posting import Posting
import os
import sys
import indexer as ind
import lexicon as lex


# TODO: multithreading to search indices in different lexical ranges at the same time?
# Returns a list of postings where all terms appeared
# The score of each positing is the sum of the scores of the postings for each term
def searchQuery(query, index, lexicon):
    query = tk.tokenize(query)
    indexItems = []
    tokenDocFreq = dict()
    postingList = []

    for token in query:
        # (token, doc_freq, posting_list)
        indexItems.append(searchToken(token, index, lexicon))

        indexItem = searchToken(token, index, lexicon)
        # token --> doc_freq
        tokenDocFreq[indexItem[0]] = indexItem[1]
        # List of postings
        postingList.append(indexItem[2])

    # AND the postings lists
    intersectIndexItems(indexItems)

    # Return only urls of sites that have ALL the query words
    # At this point, list with lists as elements changes to a single list of postings
    if len(query) > 1:
        # [posting_list, posting_list, ... ]
        postingList = mergePostingLists(postingList)
    else:
        postingList = postingList[0]

    # Compute the tf-idf

    return sorted(postingList, key=lambda t: t.score, reverse=True)


def searchToken(token, index, lexicon):
    # Check if the token searched for is in the lexicon
    if token in lexicon:
        # Seek to the place in the file that the lexicon specifies
        index.seek(lexicon[token])

        # Read the line and split it on spaces
        line = index.readline()
        return sz.deserializeIndexItem(line)
    else:
        return token, 0, []


def intersectIndexItems(indexItems):
    if len(indexItems) > 1:
        # Intersect the first two posting lists
        intersectTwoPostingsLists([indexItems[0][2]], [indexItems[1][2]])

        # If there are three or more posting lists, intersect those as well
        if len(indexItems) > 2:
            prevItems = [indexItems[0][2], indexItems[1][2]]
            for item in indexItems[2:]:
                intersectTwoPostingsLists(prevItems, [item[2]])
                prevItems.append(item[2])

        # i = 0
        # for item in indexItems:
        #     print(f"Outputting to file post{i}.txt")
        #     fileOut = open(f"post{i}.txt", "w")
        #     for post in item[2]:
        #         fileOut.write(f"{post.document}\n")
        #     fileOut.close()
        #     i += 1


def intersectTwoPostingsLists(list1, list2):
    index = 0

    # Make sure list1 has the smaller list
    if len(list1[0]) > len(list2[0]):
        temp = list1
        list1 = list2
        list2 = temp

    while index < len(list1[0]):
        # Loop through the second list until a posting is found that is greater than or equal to the current post
        while index < len(list2[0]) and list2[0][index].document < list1[0][index].document:
            for li in list2:
                li.pop(index)

        # Check to make sure there are enough elements in the second list
        if index < len(list2[0]):
            # If the documents are equal, advance the index
            if list1[0][index].document == list2[0][index].document:
                index += 1
            # If the documents are unequal, remove those items
            else:
                for li in list1:
                    li.pop(index)
                for li in list2:
                    li.pop(index)

    # For each list in the second list, slice off the excess
    if index < len(list2[0]):
        for i in range(len(list2)):
            del list2[i][index:]

# Merge two posting lists together and sort them least to greatest
def mergeTwoPostingLists(list1, list2):
    newList1 = []
    newList2 = []
    i = 0

    # Make sure list1 has the smaller list
    if len(list1) > len(list2):
        temp = list1
        list1 = list2
        list2 = temp

    # Loop through the postings in the first list
    for post in list1:
        # Loop through the second list until a posting is found that is greater than or equal to the current post
        while i < len(list2) and list2[i].document < post.document:
            i += 1

        # If the two documents are equal, add it to the return list
        if i < len(list2) and post.document == list2[i].document:
            newList1.append(post)
            newList2.append(list2[i])
            i += 1

    return newList1, newList2


def mergePostingLists(postingLists):
    # Sort the postings lists smallest to largest
    postingLists = sorted(postingLists, key=lambda l: len(l))

    # Merge the first two postings lists
    ret = mergeTwoPostingLists(postingLists[0], postingLists[1])

    postingLists[0] = ret[0]
    postingLists[1] = ret[1]

    if len(postingLists) > 2:
        for postingList in postingLists[2:]:
            ret = mergeTwoPostingLists(ret, postingList)

    return ret


def resultString(query, results, t):
    string = f"Results for query: '{query}'\n"
    string += f"Completed in {t} secs\n"
    string += f"Total results: {len(results)}\n"

    size = min(5, len(results))

    if size > 0:
        string += f"Top results:\n"
        for i in range(size):
            string += f"{results[i].document}\n"
    else:
        string += "No results found\n"

    return string


def checkBuildData():
    print("Checking if index and lexicon data exist...")

    if not os.path.exists("index.txt"):
        print("The index has not been built yet!  Building index and lexicon...")
        ind.main()
        lex.main()

    if not os.path.exists("lexicon.txt"):
        print("The lexicon has not been built yet!  Building the lexicon...")
        lex.main()


if __name__ == "__main__":
    print("Welcome to our searching engine!")

    checkBuildData()

    userInput = "not x"
    fout = open("searchReport.txt", "w")
    indexFile = open("index.txt", "r")
    watch = Stopwatch()

    print("Getting lexicon for faster searching...")
    watch.restart()
    theLex = readLexicon("lexicon.txt")
    print(f"Finished reading lexicon in {watch.read()} secs")

    currentArg = 1

    while userInput != "x":
        if currentArg < len(sys.argv):
            print("Retrieving query from command line")
            userInput = sys.argv[currentArg]
            currentArg += 1
        else:
            userInput = input("Enter the terms to search for (type 'x' to exit): ")

        if userInput != "x":
            print(f"Searching query '{userInput}'...")
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

    fout.close()
