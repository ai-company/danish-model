from typing import Sequence
from . import explain
from diff_token import *
from itertools import chain, islice, tee
from copy import copy, deepcopy

LISTING_TERMINATORS = ["og", "eller", "samt", "plus", "osv.", "m.fl.", "etc.", ""]


def clean_token_text(text):
    return text.replace(",", "").replace(".", "").replace(";", "").strip()


def insert_simple_listings(tokens, diff):
    explanation = ["Tilføj opremsningskomma."]
    new_diff = []

    tokens = DiffToken.from_spacy_list(tokens)

    # look for a sequence of equal TYPE (pos_) ending with a LISTING_TERMINATOR
    i = 0
    while i < len(tokens):
        sequence_type = tokens[i].lexeme.pos_
        from_ = to_ = i
        has_quoted_word = False

        # look ahead for sequence with same word classes
        # TODO: clean up loop condition
        while to_ < (len(tokens) - 1) and (
            tokens[to_].lexeme.pos_ == sequence_type
            or tokens[to_].lexeme.type == LexemeType.SPAC
            or (
                (to_ + 2) < len(tokens)
                and tokens[to_].lexeme.text in ('"', "'")
                and tokens[to_ + 1].lexeme.pos_ == sequence_type
                and tokens[to_ + 2].lexeme.text in ('"', "'")
            )
        ):
            if (
                (to_ + 2) < len(tokens)
                and tokens[to_].lexeme.text in ('"', "'")
                and tokens[to_ + 1].lexeme.pos_ == sequence_type
                and tokens[to_ + 2].lexeme.text in ('"', "'")
            ):
                has_quoted_word = True
                to_ += 3
            else:
                to_ += 1
                
        # if the sequence ended on a terminator, add commas
        if to_ < len(tokens) and tokens[to_].lexeme.text in LISTING_TERMINATORS:
            commas = []

            quoted_word = False
            for i, t in zip(range(from_, to_), tokens[from_:to_]):
                if has_quoted_word and t.lexeme.text == '"' and quoted_word == False:
                    # start of quoted word
                    quoted_word = True
                    commas.append(t)

                elif has_quoted_word and t.lexeme.text == '"' and quoted_word == True:
                    # end of quoted word
                    quoted_word = False
                    commas.append(t.stripped() if i < to_ - 1 else t)
                    commas.append(
                        DiffPunc(
                            ",",
                            None,
                            explanation,
                            t.lexeme.space,
                            None,
                            "add",
                            "," + t.lexeme.space,
                        )
                    )

                elif has_quoted_word and quoted_word:
                    commas.append(t)

                else:
                    commas.append(t.stripped() if i < to_ - 1 else t)
                    commas.append(
                        DiffPunc(
                            ",",
                            None,
                            explanation,
                            t.lexeme.space,
                            None,
                            "add",
                            "," + t.lexeme.space,
                        )
                    )

            # drop last extraneous comma, because everything's in pairs
            new_diff.extend(commas[:-1])

            i = to_
        else:
            # if not a sequence, just keep the token
            new_diff.append(tokens[i].clone())
            i += 1

    # reconcile diffs -------------------------------------

    i = j = 0
    while i < len(diff) and j < len(new_diff):
        if diff[i].lexeme.type == new_diff[j].lexeme.type and (
            (
                diff[i].lexeme.type == LexemeType.PUNC
                and diff[i].lexeme.text == new_diff[j].lexeme.text
            )
            or (diff[i].lexeme.type != LexemeType.PUNC)
        ):
            # print(f"match: '{diff[i]}' '{new_diff[j]}'")
            new_diff[j].index = i
            i += 1
            j += 1

        else:
            if diff[i].lexeme.type == LexemeType.PUNC and diff[i].lexeme.text == ",":
                # punctuation removal
                # print(f"remove: '{diff[i]}' '{new_diff[j]}'")
                i += 1
            elif (
                new_diff[j].lexeme.type == LexemeType.PUNC
                and new_diff[j].lexeme.text == ","
            ):
                # punctuation addition
                # print(f"add: '{diff[i]}' '{new_diff[j]}'")
                j += 1
            else:
                pprint(diff)
                pprint(new_diff)
                print(i, diff[i], j, new_diff[j])
                raise Exception("unreachable!")

    new_text = "".join(map(str, new_diff))

    return new_diff, new_text


def flag_simple_listings(diff, text, nlp):
    tokens = nlp(text)
    result_diff, result_text = insert_simple_listings(tokens, diff)

    # TODO: Double comma hack.
    # result_text = result_text.replace(", ,", ",")

    return result_diff, result_text


def heuristics(tokens, diff):
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

    result, text = insert_simple_listings(tokens, diff)

    # result = " ".join(result).replace(", ,", ",").replace(" ,", ",")

    return text
