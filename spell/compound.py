from os.path import dirname, join

import lemmy
import spacy

from . import inflect
from . import grammar
from . import explain

lemmatizer = lemmy.load("da")
path = dirname(__file__)

BINDINGS = ["s", "e", "n", ""]
COMPOUNDABLE = ["NOUN", "VERB"]

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
    lemma = lemmatizer.lemmatize(token.pos_, token.text)

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
    # TODO: Figure out dependency rules
    if token.pos_ == other.pos_ == "NOUN":
        lemma = lemmatizer.lemmatize(token.pos_, token.text)

        for word in lemma:
            if pound := compound_map.get(word):
                return pound.replace("-", other.text)
            else:
                if not "def" in token.morph.definite_:
                    return simple_connect(token.text) + other.text

    return None


def compound_words(text, changes, nlp) -> str:
    tokens = nlp(text)

    result = dict()
    last_compounded = (-2, -2)  # Index of token, index in result

    result_text = []

    for i, token in enumerate(tokens):

        result_text.append(token.text)

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

                    kwargs["singularize"] = grammar.is_singular(other)
                    kwargs["pluralize"] = not kwargs["singularize"]

                left = lemmatizer.lemmatize(token.pos_, token.text)[0]
                right = lemmatizer.lemmatize(other.pos_, other.text)[0]

                c = f"{left}{binding}{right}"

                if c in compounds:
                    right_inflected = inflect_func(other, **kwargs)
                    compound = c.replace(right, right_inflected)

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

    new_changes = []
    new_result_text = []

    last_change_i = 0

    for start, v in result.items():
        origin_map = change_map[start : v[1] + 1]
        new_changes += changes[last_change_i : origin_map[0][1]]
        new_result_text += result_text[last_change_i : origin_map[0][1]]

        last_change_i = origin_map[-1][1] + 1

        origin = []

        for index, (word, i, split_i) in enumerate(origin_map):
            if changes[i]["type"] != "split":
                origin.append(word)

        new_changes.append(
            explain.explain("merge", origin, v[0], "Disse ord bør sammensættes.")
        )

        new_result_text.append(v[0])

    if len(new_result_text) == 0:
        new_result_text = result_text
        new_changes = changes
    else:
        new_changes += changes[last_change_i : len(changes)]
        new_result_text += result_text[last_change_i : len(changes)]

    return " ".join(new_result_text).replace(" ,", ",").replace(" .", "."), new_changes


if __name__ == "__main__":
    nlp = spacy.load("da_core_news_lg")
    while True:
        text = input("> ")
        print(compound_words(text, [], nlp))
