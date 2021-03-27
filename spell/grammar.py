import spacy
import lemmy

from spacy.symbols import nsubj, VERB, ADJ
from nltk import Tree

from . import inflect
from . import explain

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


def double_check_singular(token):
    return True  # TODO: Irregular things.


def is_inconsistent(token, relative):
    if relative.morph.number_ == '':
        return double_check_singular(relative) != is_singular(token)

    return is_singular(relative) != is_singular(token)


def make_consistent(token, relative):
    if token.pos_ != 'AUX' and 'inf' in relative.morph.verb_form_:
        abort_mission = False
        for t in relative.children:
            if t.dep_ == 'aux':
                abort_mission = True
                break

        if not abort_mission:
            correct = inflect.inflect_verb(relative, presentize=True)
            # print(token.text, relative.text, f'-> `{correct}`')

            return correct, relative.i, 'Forveksling af infinitiv og nutid.'

    elif token.pos_ == 'AUX'\
            and 'inf' not in relative.morph.verb_form_:
        correct = inflect.inflect_verb(relative)
        # print(token.text, relative.text, f'-> `{correct}`')

        return correct, relative.i, 'Forveksling af infinitiv og nutid.'

    elif token.pos_ == 'DET' and token.text in ['en', 'et']:
        if token.morph.gender_ != relative.morph.gender_:
            correct = token.text == 'et' and 'en' or 'et'
            gender = correct == 'en' and 'fælleskøn' or 'intetkøn'

            return correct, token.i, f'Substantiver af {gender} skal have artiklen "{correct}".'

    elif token.pos_ in ['PRON', 'NOUN', 'DET'] and is_inconsistent(token, relative):
        correct = relative.text + ' is wrong'
        singular = is_singular(token)

        explanation = singular and f'"{relative.text}" skal bøjes i ental her.' or f'"{relative.text}" skal bøjes i flertal her.'

        if relative.pos_ in ['PROPN', 'NOUN']:
            correct = inflect.inflect_noun(
                relative,
                singularize=singular,
                pluralize=not singular
            )

        elif relative.pos_ == 'ADJ':
            itk = 'neut' in token.morph.gender_

            correct = inflect.inflect_adj(
                relative,
                itk=itk,
                pluralize=not singular,
                singularize=singular
            )

            if itk:
                explanation = f'"{token.text}" skal bøjes i intetkøn her.'

        # print(token.text, relative.text, f'-> {correct}')

        return correct, relative.i, explanation

    elif token.pos_ == 'ADJ' and is_inconsistent(token, relative):
        singular = is_singular(relative)
        itk = 'neut' in token.morph.gender_

        correct = inflect.inflect_adj(
            token,
            itk=itk,
            singularize=singular,
            pluralize=not singular
        )

        if itk:
            explanation = f'"{token.text}" skal bøjes i intetkøn her.'
        else:
            explanation = singular and f'"{token.text}" skal bøjes i ental her.' or f'"{token.text}" skal bøjes i flertal her.'

        # print(token.text, relative.text, f'-> `{correct}`')

        abort_mission = False

        for t in relative.children:
            if t.dep_ == 'det' and singular and 'plur' in t.morph.number_:
                abort_mission = True

        if not abort_mission:
            return correct, token.i, explanation

    elif token.pos_ == 'VERB' and relative.dep_ == 'nsubj':
        correct = inflect.inflect_verb(token, presentize=True)
        # print(token.text, relative.text, f'-> `{correct}`')

        return correct, token.i, 'Forveksling af infinitiv og nutid.'

    return token, None, ''


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
        'det':   [t for t in siblings(token) if t.pos_ in ['ADJ', 'NOUN', 'PROPN']],
        'amod':  [token.head],
        'aux':   [token.head],
        'xcomp': [t for t in siblings(token) if t.dep_ == 'nsubj']
    }.get(token.dep_.lower())


def init():
    nlp = spacy.load('da_core_news_lg')

    def fix(text, changes=None):
        doc = nlp(text)

        fix_map = dict()  # For inserting fixes in corrected string.
        result = []      # List of corrected words for corrected string.

        # print()

        for token in doc:
            result.append(token.text)
            # print()
            # print(
            #     f'{token.text}({token.pos_}) @ {token.dep_} & {token.morph.to_json()}')

            if relatives := relatives_of(token, doc):
                for t in relatives:
                    # print(
                    #     f'    -> {t.text}({t.morph.to_json()})')

                    correct, i, explanation = make_consistent(token, t)

                    if not i is None:  # None if nothing changed. :)
                        explain.append_change(
                            changes, i,
                            explain.change('change', correct, explanation)
                        )

                        fix_map[i] = correct

        # print()
        # draw_tree(doc)
        # print()

        for i, word in fix_map.items():
            result[i] = word

        return ' '.join(result), changes

    return fix


if __name__ == "__main__":
    fix = init()
    while True:
        text = input()
        print(fix(text))
