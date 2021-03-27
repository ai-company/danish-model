import spacy
import collections
import tqdm

from os.path import join, dirname
from sys import argv

bindings = [
    'og', 'men', 'eller', 'samt', 'for', 'thi',
    'både', 'at', 'da', 'dengang', 'end', 'efter', 'for', 'fordi',
    'før', 'hvorvidt', 'idet', 'ifald', 'indtil', 'jo', 'ligesom',
    'medmindre', 'mens', 'når', 'om', 'selv', 'siden', 'skønt',
    'som', 'så', 'såfremt', 'snart', 'til', 'uden', 'ved', 'm.fl.',
    'selvom', 'inden', 'hallo', 'av', 'halløj', 'hey', 'eow', 'hej', 'goddag', 'godaften',
    'især', 'men', 'bare', 'selvom', 'dog', 'herunder', 'heriblandt', 'såsom', 'e.g.', 'eksempelvis', 'f.eks.'
]


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


def mask(t):
    if (str(t.pos_) in ['PROPN', 'NOUN', 'SYM', 'ADJ']) and (t.text.lower() not in bindings):
        return make_tag(t.tag_)

    return str(t.text)


def maybe_comma(t):
    if t.text == ',':
        return ','

    return mask(t)


if __name__ == "__main__":
    nlp = spacy.load("da_core_news_lg")

    print(f'Reading {argv[1]} and making {argv[2]}')

    with open(argv[1], 'r') as in_f, open(argv[2], 'a') as out_f:
        lines = in_f.readlines()
        for line in tqdm.tqdm(lines):
            doc = nlp(line)
            doc = ' '.join([maybe_comma(t) for t in doc])

            out_f.write(f'{doc}\n')
