from os.path import dirname, join

import spacy
from . import grammar
import lemmy
import random

lemmatizer = lemmy.load('da')


def load_inflections(path):
    inflections = dict()
    with open(path, 'r') as f:
        for line in f:
            line = line.split('\t')
            parts = [p.strip() for p in line[1].split(',')]

            inflections[line[0].strip()] = parts

    return inflections


noun_inflections = load_inflections(
    join(dirname(__file__), 'inflections_noun.txt'))

verb_inflections = load_inflections(
    join(dirname(__file__), 'inflections_verb.txt'))

adj_inflections = load_inflections(
    join(dirname(__file__), 'inflections_adj.txt'))


def inflect_noun(token, properize=False, pluralize=False, singularize=False):
    noun = lemmatizer.lemmatize('', token.text)[0]
    if inflections := noun_inflections.get(noun):
        i = 0

        if pluralize and properize:
            i = 2
        elif pluralize:
            i = 1
        elif properize:
            i = 0
        else:
            return noun

        inflection = inflections[i]

        if 'el.' in inflection:
            inflection = random.choice(inflection.split('el.')).strip()

        return '-' in inflection and inflection.replace('-', noun) or inflection

    if '_neut' in token.morph.gender_:
        if properize:
            ending = ''

            if grammar.is_singular(token):
                ending = {
                    's': 'set',
                    'n': 'net',
                    'k': 'ket',
                    'm': 'met',
                    'p': 'pet',
                    'e': 't',
                }.get(token.text[-1], 'et')
            else:
                ending = {
                    'r': 'ne',
                    't': 'te',
                    'e': 'ne',
                }.get(token.text[-1], 'ene')

            return f'{token.text}{ending}'
    else:
        if properize:
            ending = ''

            if '_sing' in token.morph.number_:
                ending = {
                    's': 'sen',
                    'n': 'nen',
                    'k': 'ken',
                    'm': 'men',
                    'p': 'pen',
                    'e': 'n',
                }.get(token.text[-1], 'en')
            else:
                ending = {
                    'r': 'ne',
                    's': 'serne',
                    'm': 'merne',
                    'p': 'perne',
                }.get(token.text[-1], 'erne')

            return f'{token.text}{ending}'

    if pluralize:
        ending = {
            'e': 'r',
        }.get(token.text[-1], 'er')

        return f'{token.text}{ending}'

    return lemmatizer.lemmatize(token.text)[0]  # Singular cause of lemma B)


def inflect_verb(token, presentize=False, pastize=False, didize=False):
    verb = lemmatizer.lemmatize('', token.text)[0]
    if inflections := verb_inflections.get(verb):
        i = 0

        if presentize:
            i = 0
        elif pastize:
            i = 1
        elif didize:
            i = 2
        else:
            return verb

        inflection = inflections[i]

        if 'el.' in inflection:
            inflection = random.choice(inflection.split('el.')).strip()

        return '-' in inflection and inflection.replace('-', verb) or inflection

    if presentize:
        return f'{token.text}r'  # Now times R

    if pastize:
        ending = {
            'e': 'de',
        }.get(token.text[-1], 'ede')

        return f'{token.text}{ending}'

    return verb


def inflect_adj(token, itk=False, pluralize=False, singularize=False):
    adj = lemmatizer.lemmatize('', token.text)[0]
    if inflections := adj_inflections.get(adj):
        i = 0
        if len(inflections) == 1 and pluralize:
            i = 0
        else:
            if pluralize:
                i = 1
            elif itk:
                i = 0
            else:
                return adj

        inflection = inflections[i]

        if 'el.' in inflection:
            choices = inflection.split('el.')

            if 'itk. d.s.' in choices:
                inflection = choices[1].strip()
            else:
                inflection = random.choice(choices).strip()
        elif 'itk. d.s.' in inflection:
            inflection = adj

        return '-' in inflection and inflection.replace('-', adj) or inflection

    if pluralize:
        ending = {
            'e': 'de',
            'n': 'ne',
            't': 'te',
            'm': 'me',
            's': 'se',
            'p': 'pe',
        }.get(token.text[-1], 'e')

        return f'{token.text}{ending}'
    elif itk:
        return f'{token.text}t'

    return adj


if __name__ == "__main__":
    nlp = spacy.load('da_core_news_lg')
    while True:
        text = input('> ')
        for token in nlp(text):
            print(token.morph.gender_, token.pos_,
                  lemmatizer.lemmatize('', token.text))
            print(inflect_adj(token, pluralize=True))
