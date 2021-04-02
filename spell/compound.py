from os.path import dirname, join

import lemmy
import spacy

from . import inflect
from . import grammar
from . import explain

lemmatizer = lemmy.load("da")
path = dirname(__file__)

BINDINGS = ["s", "e", "n", ""]
COMPOUNDABLE = ["NOUN", "ADJ", "VERB"]

with open(join(path, "compounds.txt")) as f:
    compounds = [line.strip() for line in f]

with open(join(path, "compound_map.txt")) as f:
    compound_map = dict()

    for line in f:
        line = line.split("\t")
        compound_map[line[0]] = line[1]

compound_values = [x.replace("-", "") for x in compound_map.values()]


def simple_connect(text):
    doubles = {
        "st": "e",
    }

    if e := doubles.get(text[-2:]):
        ending = e
    else:
        ending = {
            "g": "ge",
            "t": "te",
            "n": "ne",
            "k": "ke",
            "l": "le",
            "s": "se",
            "e": "",
        }.get(text[-1], "e")

    return f"{text}{ending}"


def should_compound_straight(token, other, nlp):
    lemma = lemmatizer.lemmatize("NOUN", token.text)

    result = False

    if token.pos_ in COMPOUNDABLE and other.pos_ in COMPOUNDABLE:

        for word in lemma:
            in_compounds = token.text in compound_values + [simple_connect(word)]

            if nlp(word)[0].pos_ != token.pos_ or in_compounds and word != token.text:

                if c := in_compounds:
                    result = c
                    break

    return result


def check_compound(token, other, nlp):
    # (token.pos_ == other.pos_ == "NOUN") or
    if (
        token.pos_ in COMPOUNDABLE
        and not (token.pos_ == other.pos_ == "VERB")
        and token.dep_ != "ROOT"
    ):
        lemma = lemmatizer.lemmatize(token.pos_, token.text)

        for word in lemma:
            if pound := compound_map.get(word):
                return pound.replace("-", other.text)
            else:
                return simple_connect(token.text) + other.text

    return None


def compound_words(text, changes, nlp) -> str:
    tokens = nlp(text)

    result = dict()
    last_compounded = (-2, -2)  # Index of token, index in result

    for i, token in enumerate(tokens):
        if i < len(tokens) - 1:
            other = tokens[i + 1]
            add_to_last = last_compounded[0] == i - 1

            if add_to_last:
                token_ = nlp(result[last_compounded[1]][0])[0]
            else:
                token_ = token

            compound = None

            for binding in BINDINGS:
                kwargs = {}

                inflect_func = None

                if other.pos_ == "VERB":
                    tense = other.morph.tense_
                    inflect_func = inflect.inflect_verb

                    kwargs["pastize"] = "past" in tense
                    kwargs["didize"] = (
                        "past" in tense and "part" in other.morph.verb_form_
                    )
                    kwargs["presentize"] = "pres" in tense

                elif other.pos_ == "NOUN":

                    inflect_func = inflect.inflect_noun

                    kwargs["singularize"] = grammar.is_singular(other)
                    kwargs["pluralize"] = not kwargs["singularize"]
                    kwargs["properize"] = "yes" in other.morph.poss_

                elif other.pos_ == "ADJ":

                    inflect_func = inflect.inflect_adj

                    kwargs["singularize"] = grammar.is_singular_adj(other)
                    kwargs["pluralize"] = not kwargs["singularize"]

                left = lemmatizer.lemmatize(token.pos_, token.text)[0]
                right = lemmatizer.lemmatize(other.pos_, other.text)[0]

                c = f"{left}{binding}{right}"

                if c in compounds:
                    right_inflected = inflect_func(other, **kwargs)
                    compound = c.replace(right, right_inflected)

                    print(compound)

            if not compound:
                if should_compound_straight(token_, other, nlp):
                    if add_to_last:
                        compound = f"{result[last_compounded[1]][0]}{other.text}"
                    else:
                        compound = f"{token.text}{other.text}"
                else:
                    if add_to_last:
                        if c := check_compound(
                            nlp(result[last_compounded[1]][0])[0], other, nlp
                        ):
                            compound = c
                        else:
                            continue
                    else:
                        if c := check_compound(token_, other, nlp):
                            compound = c
                        else:
                            continue

            if add_to_last:
                result[last_compounded[1]] = (compound, other.i)
                last_compounded = (i, last_compounded[1])
            else:
                result[i] = (compound, other.i)
                last_compounded = (i, i)

    # Manage changes

    change_map = explain.change_map(changes)

    for start, v in result.items():
        origin = change_map[start : v[1]]

        print(origin)

    return result, changes


if __name__ == "__main__":
    nlp = spacy.load("da_core_news_lg")
    while True:
        text = input("> ")
        print(compound_words(text, [], nlp))
