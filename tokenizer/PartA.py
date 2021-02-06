import sys
import re


# opens text file and look at each char, reconstructs text and returns a list of tokens. 
# runtime: O(n^2) as there is a double for loop checking the validity of each char.
def tokenize(s):

    tokens = []
    raw_tokens = re.split(r'[^\w\d]+', s)

    for text in raw_tokens:
        temp = ''
        for char in text:
            if re.match("^[A-Za-z0-9]*$", char):
                temp += char
        if len(temp) > 0:
            tokens.append(temp.lower())
            
    return tokens


# count the numbers of each word and returns them in a dictionary 
# runtime: O(n) looks through the list of tokens once
def computeWordFrequencies(token_list):
    
    token_count = {}

    for t in token_list:
        if t not in token_count:
            token_count[t] = 1
        else:
            token_count[t] += 1
    
    return token_count


# sorts the dictionary by value decending
# runtime: O(n) looks through the sorted list of tokens once
def frequencies(token_dict):

    sorted_token = sorted(token_dict.items(), key = lambda x:x[1], reverse = True)
    
    for pair in sorted_token:
        print(f'{pair[0]} {pair[1]}')
   

if __name__ == "__main__":
    token_list = tokenize(1)
    token_dict = computeWordFrequencies(token_list)
    frequencies(token_dict)
