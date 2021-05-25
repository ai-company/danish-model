from typing import Sequence
from . import explain
from diff_token import *
from pprint import pprint
from itertools import chain, islice, tee
from copy import copy, deepcopy

LISTING_TERMINATORS = ["og", "eller", "samt", "plus", "osv.", "m.fl.", "etc.", ""]


def clean_token_text(text):
    return text.replace(",", "").replace(".", "").replace(";", "").strip()


def spacy_to_canon(tokens):
    canon = []

    for i, token in enumerate(tokens):
        if token.pos_ == "SPACE":
            canon[-1].space += token.text
        else:
            canon.append(
                DiffToken(
                    token.text,
                    token.text,
                    DiffTokenType.from_pos(token.pos_),
                    i,
                    [],
                    token.whitespace_,
                    token.pos_,
                )
            )

    return canon


def insert_simple_listings(tokens, changes=None):
    explanation = ["Tilføj opremsningskomma."]
    new_diff = []

    tokens = spacy_to_canon(tokens)

    # TODO: map new diff to old diff

    # look for a sequence of equal TYPE (pos_) ending with a LISTING_TERMINATOR
    i = 0
    while i < len(tokens):
        sequence_type = tokens[i].pos_
        from_ = to_ = i

        # look ahead for sequence with same word classes
        while to_ < (len(tokens) - 1) and tokens[to_].pos_ == sequence_type:
            to_ += 1

        # if the sequence ended on a terminator, add commas
        if tokens[to_].text in LISTING_TERMINATORS:
            commas = []

            for i, t in zip(range(from_, to_), tokens[from_:to_]):
                commas.append(t.stripped() if i < to_ - 1 else t)
                commas.append(DiffPunc(",", t.index, explanation, t.space))

            # drop last extraneous comma, because everything's in pairs
            new_diff.extend(commas[:-1])

            i = to_
        else:
            # if not a sequence, just keep the token
            new_diff.append(tokens[i])
            i += 1

    new_text = "".join(map(lambda t: t.text + t.space, new_diff))

    return new_diff, new_text


def flag_simple_listings(diff, text, nlp):
    tokens = nlp(text)
    result_diff, result_text = insert_simple_listings(tokens, diff)

    # TODO: Double comma hack.
    result_text = result_text.replace(", ,", ",")

    return result_diff, result_text


def heuristics(tokens):
    """
    Heuristics for catching low-hanging fruits with 100% accuracy.

    Params:
        - tokens: A list of spaCy tokens for the most recent pass.

    Returns:
        - result: Text result.
    """
    result = []

    start = " ".join([t.text for t in tokens])

    for i, token in enumerate(tokens):
        if token.text in ["der", "som"] and token.dep_ == "nsubj":
            result.append(",")
        elif token.text == "at":
            if i + 1 < len(tokens):
                if i != len(tokens) and "inf" not in tokens[i + 1].morph.verb_form_:
                    result.append(",")
        elif i != 0 and token.text == "men" and token.pos_ != "NOUN":
            result.append(",")

        result.append(token.text)

    result = insert_simple_listings(tokens, result)

    result = " ".join(result).replace(", ,", ",").replace(" ,", ",")

    return result
