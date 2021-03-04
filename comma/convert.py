import spacy

import collections
import sys

nlp = spacy.load("da_core_news_lg")

def make_tag(t):
    result = ''

    t = t.split('__')

    result += t[0][:2]

    t = str(t[1:]).split('|')

    hash = {}

    for n in t:
        if '=' in n:
            ass = n.split('=')
            hash[ass[0]] = ass[1]

    hash = collections.OrderedDict(sorted(hash.items()))
    result += ''.join([v[0] for _, v in hash.items()])

    return result

def convert(pos, original):
    result   = ''

    original = [t for t in nlp(original)]

    pos = filter(lambda x: x != '', pos.split())

    for i, t in enumerate(pos):
        t = str(t).split(',')

        result += str(original[i].text)

        if len(t) == 2:
            result += ',' 

        if original[i].whitespace_:
            result += original[i].whitespace_

    return result