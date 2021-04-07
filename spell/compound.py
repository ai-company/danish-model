from os.path import dirname, join

import lemmy
import spacy

from . import inflect
from . import grammar2 as grammar
from . import explain

lemmatizer = lemmy.load("da")
path = dirname(__file__)

BINDINGS = ["s", "e", "n", ""]
COMPOUNDABLE = ["noun", "verb"]

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


def should_compound_straight(a, b, nlp):
    lemma = lemmatizer.lemmatize(a.pos.upper(), a.text)

    result = False

    if a.pos in COMPOUNDABLE and b.pos in COMPOUNDABLE:

        for word in lemma:
            in_compounds = a.text in compound_values + [simple_connect(word)]

            if nlp(word)[0].pos_.lower() != a.pos or in_compounds and word != a.text:
                if c := in_compounds:
                    result = c
                    break

    return result


def check_compound(token, other, nlp):
    # TODO: Figure out dependency rules
    if token.pos == other.pos == "noun":
        lemma = lemmatizer.lemmatize(token.pos, token.text)

        for word in lemma:
            if pound := compound_map.get(word):
                return pound.replace("-", other.text)
            else:
                if token.has("definite", "def"):
                    return simple_connect(token.text) + other.text

    return None


def compound_words(text, changes, nlp) -> str:
    tokens = nlp(text)

    result = dict()
    last_compounded = (-2, -2)  # Index of token, index in result

    result_text = []

    for i, token in enumerate(tokens):
        go = grammar.GrammarObject.from_token(token)

        result_text.append(token.text)

        if i < len(tokens) - 1:
            other = grammar.GrammarObject.from_token(tokens[i + 1])
            add_to_last = last_compounded[0] == i - 1

            if add_to_last:
                token_ = nlp(result[last_compounded[1]][0])[0]
            else:
                token_ = token

            go_ = grammar.GrammarObject.from_token(token_)

            compound = None

            for binding in BINDINGS:
                kwargs = {}

                inflect_func = None

                if other.pos == "verb":
                    tense = other["tense"] or []
                    inflect_func = inflect.inflect_verb

                    kwargs["pastize"] = "past" in tense
                    kwargs["didize"] = "past" in tense and "part" == other["verbform"]
                    kwargs["presentize"] = "pres" in tense

                elif other.pos == "noun":

                    inflect_func = inflect.inflect_noun

                    kwargs["singularize"] = grammar.is_singular(other)
                    kwargs["pluralize"] = not kwargs["singularize"]
                    kwargs["properize"] = other.has("poss", "yes")

                elif other.pos == "adj":

                    inflect_func = inflect.inflect_adj

                    kwargs["singularize"] = grammar.is_singular(other)
                    kwargs["pluralize"] = not kwargs["singularize"]

                lefts = lemmatizer.lemmatize(go.pos, go.text) + [go.text]
                rights = lemmatizer.lemmatize(other.pos.upper(), other.text) + [
                    other.text
                ]

                for left in lefts:
                    for right in rights:
                        c = f"{left}{binding}{right}"

                        if c in compounds:
                            # Compounds are inflected by their last element.
                            right_inflected = inflect_func(
                                other,
                                lemma=right,
                                **kwargs,
                            )
                            compound = c.replace(right, right_inflected)

                            if go.dep == "root" and nlp(compound)[0].pos_ != "VERB":
                                compound = None
                                continue
                            else:
                                break

                    if compound:
                        break

            if not compound:
                if should_compound_straight(go_, other, nlp):
                    if add_to_last:
                        compound = f"{result[last_compounded[1]][0]}{other.text}"
                    else:
                        compound = f"{go.text}{other.text}"
                else:
                    if add_to_last:
                        if c := check_compound(
                            nlp(result[last_compounded[1]][0])[0], other, nlp
                        ):
                            compound = c
                        else:
                            continue
                    else:
                        if c := check_compound(go_, other, nlp):
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

        # print("[comp] -", start, v)
        # import pdb

        # pdb.set_trace()

        last_change_i = v[1] + 1  # origin_map[-1][1] + 1

        origin = []

        for index, (word, i, split_i) in enumerate(origin_map):
            if changes[i]["type"] == "split":
                if c := changes[i]["change"][split_i]:
                    if c["type"] == "none":
                        origin.append(c["origin"])
                    else:
                        origin.append(c["change"])
            else:
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
