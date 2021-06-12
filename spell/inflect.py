from os.path import dirname, join

import spacy
from . import grammar
import lemmy
import random

lemmatizer = lemmy.load("da")


def load_inflections(path):
    inflections = dict()
    with open(path, "r") as f:
        for line in f:
            line = line.split("\t")
            parts = [p.strip() for p in line[1].split(",")]

            inflections[line[0].strip()] = parts

    return inflections


noun_inflections = load_inflections(join(dirname(__file__), "inflections_noun.txt"))
verb_inflections = load_inflections(join(dirname(__file__), "inflections_verb.txt"))
adj_inflections = load_inflections(join(dirname(__file__), "inflections_adj.txt"))


def inflect_noun(go, properize=False, pluralize=False, singularize=False, lemma=None):
    noun = lemma or lemmatizer.lemmatize("NOUN", go.text)[0]

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

        if len(inflections) > i:
            inflection = inflections[i]

            if "el." in inflection:
                inflection = random.choice(inflection.split("el.")).strip()

            return "-" in inflection and inflection.replace("-", noun) or inflection

    if go.has("gender", "neut"):
        if properize:
            ending = ""

            if grammar.is_singular(go):
                ending = {
                    "s": "set",
                    "n": "net",
                    "k": "ket",
                    "m": "met",
                    "p": "pet",
                    "e": "t",
                }.get(go.text[-1], "et")
            else:
                ending = {
                    "r": "ne",
                    "t": "te",
                    "e": "ne",
                }.get(go.text[-1], "ene")

            return f"{go.text}{ending}"
    else:
        if properize:
            ending = ""

            if go.has("number", "sing"):
                ending = {
                    "s": "sen",
                    "n": "nen",
                    "k": "ken",
                    "m": "men",
                    "p": "pen",
                    "e": "n",
                }.get(go.text[-1], "en")
            else:
                ending = {
                    "r": "ne",
                    "s": "serne",
                    "m": "merne",
                    "p": "perne",
                }.get(go.text[-1], "erne")

            return f"{go.text}{ending}"

    if pluralize:
        ending = {
            "e": "r",
        }.get(go.text[-1], "er")

        return f"{go.text}{ending}"

    return noun  # Singular cause of lemma B)


def inflect_verb(go, presentize=False, pastize=False, didize=False, lemma=None):
    verb = lemma or lemmatizer.lemmatize("VERB", go.text)[0]
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

        if "el." in inflection:
            inflection = random.choice(inflection.split("el.")).strip()

        return "-" in inflection and inflection.replace("-", verb) or inflection

    if presentize:
        return f"{go.text}r"  # Now times R

    if pastize:
        ending = {
            "e": "de",
        }.get(go.text[-1], "ede")

        return f"{go.text}{ending}"

    return verb


def inflect_adj(go, itk=False, pluralize=False, singularize=False, lemma=None):
    adj = lemma or lemmatizer.lemmatize("ADJ", go.text)[0]
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

        if "el." in inflection:
            choices = inflection.split("el.")

            if "itk. d.s." in choices:
                inflection = choices[1].strip()
            else:
                inflection = random.choice(choices).strip()
        elif "itk. d.s." in inflection:
            inflection = adj

        return "-" in inflection and inflection.replace("-", adj) or inflection

    if pluralize:
        ending = {
            "e": "de",
            "n": "ne",
            "t": "te",
            "m": "me",
            "s": "se",
            "p": "pe",
        }.get(go.text[-1], "e")

        return f"{go.text}{ending}"
    elif itk:
        if go.text[-1] != "t":
            return f"{go.text}t"

    return adj


def inflect(go, **kwargs):
    return {
        "NOUN": inflect_noun(go, **kwargs),
        "ADJ": inflect_adj(go, **kwargs),
        "VERB": inflect_verb(go, **kwargs),
    }.get(go.pos)


if __name__ == "__main__":
    nlp = spacy.load("da_core_news_lg")
    while True:
        text = input("> ")
        for token in nlp(text):
            print(token.morph.gender_, token.pos_, lemmatizer.lemmatize("", token.text))
            print(inflect_adj(grammar.GrammarObject.from_token(token), pluralize=True))
