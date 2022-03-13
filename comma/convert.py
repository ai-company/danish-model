import spacy
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


def convert(pos, original, nlp):
    result = ""

    original = [t for t in nlp(original)]

    # pprint(list(pos.split()))
    # pprint(original)
    pos = list(filter(lambda x: x != "", pos.split()))
    # (pprint(list(enumerate(zip(pos, [f"[{o.tag_} {o.text}]"  for o  in original])))))

    # for i, t in enumerate(pos):
    #     t = str(t).split(",")

    #     result += str(original[i].text)

    #     if len(t) == 2:
    #         result += ","

    #     if original[i].whitespace_:
    #         result += original[i].whitespace_

    # i = j = 0
    # hadComma = False
    # while i < len(original) and j < len(pos):
    #     if not hadComma and len(comma := pos[j].split(",")) > 1:
    #         hadComma = True
    #         if comma[0] != "":
    #             result += original[i].text
    #             result += ","
    #             if original[i].whitespace_:
    #                 result += original[i].whitespace_
    #             i += 1
    #             j += 1
    #         else:
    #             result += ","
    #             if original[i].whitespace_:
    #                 result += original[i].whitespace_
    #             j += 1
    #     elif len(comma := pos[j].split(",")) > 1:
    #         j += 1
    #     else:
    #         hadComma = False
    #         result += original[i].text
    #         if original[i].whitespace_:
    #             result += original[i].whitespace_
    #         i += 1
    #         j += 1

    i = j = 0
    hadComma = False  # sometimes model produces multiple commas in the same spot, this flag ignores duplicates
    while i < len(original) and j < len(pos):
        if len(comma := pos[j].split(",")) > 1:  # we have a comma
            j += 1

            # standalone comma surrounded by spaces, ignored if we already had one prior
            # cases when ignored:
            # - type,COMMA ,COMMA
            # - ,COMMA ,COMMA
            # must not ignore:
            # - ,COMMA type,COMMA
            if comma[0] == "":
                if not hadComma:
                    hadComma = True
                    result += original[i].text + ","

                    # carry over whitespace after the new punctuation
                    if original[i].whitespace_:
                        result += original[i].whitespace_

                else:  # we already saw a comma, ignore this one
                    pass

            else:  # comma postfixing a word
                hadComma = True

                result += original[i].text + ","

                # carry over whitespace after the new punctuation
                if original[i].whitespace_:
                    result += original[i].whitespace_

                i += 1

        else:  # no punctuation here, continue and reset duplicate watcher
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
