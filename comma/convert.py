from typing import List
import spacy
from spacy.language import Doc, Language
from spacy.tokens import Token
from pprint import pprint
import collections
import sys


def make_tag(t):
    result = ""

    t = t.split("__")

    result += t[0][:2]

    t = str(t[1:]).split("|")

    hash = {}

    for n in t:
        if "=" in n:
            ass = n.split("=")
            hash[ass[0]] = ass[1]

    hash = collections.OrderedDict(sorted(hash.items()))
    result += "".join([v[0] for _, v in hash.items()])

    return result


def convert(pos: str, original: str, nlp: Language):
    result = ""

    # tokenize sentence
    original: List[Token] = list(nlp(original))

    # filter out empty pieces
    pos: List[str] = list(filter(lambda x: x != "", pos.split()))

    i = j = 0
    hadComma = False  # sometimes model produces multiple commas in the same spot, this flag ignores duplicates
    hadPunct = False  # comma must not be before or after punctuation

    while i < len(original) and j < len(pos):
        if len(comma := pos[j].split(",")) > 1:  # we have a comma
            j += 1

            # standalone comma surrounded by spaces, ignored if we already had one prior
            #
            # cases when ignored:
            # - type,COMMA ,COMMA
            # - ,COMMA ,COMMA
            # - punc ,COMMA
            #
            # must not ignore:
            # - ,COMMA type,COMMA
            if comma[0] == "" or comma[0] == "_s":
                if not hadComma and not hadPunct:
                    hadComma = True
                    result += original[i].text + ","

                    # carry over whitespace after the new punctuation
                    if original[i].whitespace_:
                        result += original[i].whitespace_

                    if comma[0] == "_s":
                        i += 1
                else:  # we already saw a comma or punct, ignore this one
                    # print("comma: {hadComma} punct: {hadPunct}")
                    i += 1
                    pass

            else:  # comma postfixing a word
                hadComma = True

                result += original[i].text + ","

                # carry over whitespace after the new punctuation
                if original[i].whitespace_:
                    result += original[i].whitespace_

                i += 1

        else:  # no punctuation here, continue and reset duplicate watcher
            hadPunct = original[i].pos_ == "PUNCT"

            if hadPunct:
                pass

            if hadComma and hadPunct:  # comma before punct
                pass
                # print("comma_------------------------------------------")

            hadComma = False

            result += original[i].text
            if original[i].whitespace_:
                result += original[i].whitespace_

            i += 1
            j += 1

    return result


# noun, noun
# noun,noun
# noun , noun
