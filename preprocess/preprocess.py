
import os
import codecs
import re
import sys
import nltk

# nltk.download('punkt')
from nltk.tokenize import word_tokenize

NUM    = "<NUM>"
PUNCTS = {",": ",COMMA", }

forbidden_symbols = re.compile(r"[\[\]\(\)\/\\\>\<\=\+\_\*]")
numbers           = re.compile(r"\d")
punct             = re.compile(r"([\.\?\!\,\:\;\-])(?:[\.\?\!\,\:\;\-]){1,}")

def is_number(x):
    if len(x) == 0:
        return False

    return len(numbers.sub("", x)) / len(x) < 0.6

def skip(line):
    if line.strip() == "":
        return True

    last_symbol = line[-1]

    return False

def process_line(line):
    tokens = line.split(" ")
    output_tokens = []

    for token in tokens:
        if token in PUNCTS:
            output_tokens.append(PUNCTS[token])
        elif is_number(token):
            output_tokens.append(NUM)
        else:
            output_tokens.append(token.lower())

    return ' '.join(output_tokens) + ' '

if __name__ == "__main__":
    skipped = 0

    with codecs.open(sys.argv[2], "w", encoding="utf-8") as out_txt, \
         codecs.open(sys.argv[1], "r", encoding="utf-8") as text:

        for line in text:

            line = line.replace('"', "").strip()
            line = punct.sub(r"\g<1>", line)

            if skip(line):
                skipped += 1
                continue

            line = process_line(line)

            out_txt.write(line + "\n")

    print("Skipped {} lines".format(skipped))