import spacy
import lemmy

from spacy.symbols import nsubj, VERB, ADJ
from nltk import Tree

lemmatizer = lemmy.load('da')


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


def draw_tree(doc):
    [to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]


# ======================= END OF DEBUG

def is_singular_adj(text):
    return lemmatizer.lemmatize('ADJ', text)[0] == text


def is_singular(token):
    if token.pos_ == 'ADJ':
        return is_singular_adj(token.text)
    return 'sing' in token.morph.number_


def is_inconsistent(token, relative):
    if relative.morph.number_ == '':
        return False
    return is_singular(relative) != is_singular(token)


def make_consistent(token, relative):
    if token.pos_ != 'AUX' and 'inf' in relative.morph.verb_form_:
        print(token.text, relative.text, f'-> `{relative.text}` is wrong')

    if token.pos_ in ['PRON', 'NOUN', 'DET'] and is_inconsistent(token, relative):
        print(token.text, relative.text, f'-> `{relative.text}` is wrong')

    if token.pos_ == 'ADJ' and is_inconsistent(token, relative):
        print(token.text, relative.text, f'-> `{token.text}` is wrong')


def siblings(token):
    result = token.head == token and [] or [token.head]
    for child in token.head.children:
        if child == token:
            continue

        result.append(child)

    return list(set(result))


def relatives_of(token, doc):
    return {
        'nsubj': [token.head],
        'root':  [],
        'det':   [t for t in siblings(token) if t.pos_ in ['ADJ', 'NOUN']],
        'amod':  [token.head]
    }.get(token.dep_.lower())


def init():
    nlp = spacy.load('da_core_news_lg')

    def fix(text, changes=None):
        doc = nlp(text)

        print()

        for token in doc:
            # print()
            # print(
            #     f'{token.text}({token.pos_}) @ {token.dep_} & {token.morph.to_json()}')

            if relatives := relatives_of(token, doc):
                for t in relatives:
                    # print(
                    #     f'    -> {t.text}({t.morph.to_json()})')

                    make_consistent(token, t)

        print()
        draw_tree(doc)
        # print()

    return fix


if __name__ == "__main__":
    fix = init()
    while True:
        text = input()
        fix(text)
