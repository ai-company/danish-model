from . import explain
from diff_token import DiffToken

LISTING_TERMINATORS = ["og", "eller", "samt", "plus", "osv.", "m.fl.", "etc.", ""]


def clean_token_text(text):
    return text.replace(",", "").replace(".", "").replace(";", "").strip()


def insert_simple_listings(tokens, result=[], changes=None):
    alter_changes = changes is not None

    sequence_root = None
    sequence_indices = []

    new_diff = changes[:]
    offset = 0

    # TODO: Redo in a functional and nice manner.
    # - Don't mutate the list we are iterating.
    # - Use look-ahead for the sequence pattern.
    # - If a match is found, add commas at the proper seq-interval.

    for i, token in enumerate(tokens):
        if sequence_root is None:
            sequence_root = token.pos_
        else:
            cleaned = clean_token_text(token.text.lower())
            if sequence_root and cleaned in LISTING_TERMINATORS:
                for index in sequence_indices:
                    if alter_changes:
                        new_diff.insert(
                            index + offset,
                            DiffToken(
                                ",",
                                "",
                                "punctuation",
                                new_diff[index + offset].index,
                                ["Tilføj opremsningskomma."],
                                new_diff[index + offset].space,
                            ),
                        )

                        new_diff[index + offset - 1].space = ""
                        print(
                            f'"{new_diff[index + offset - 1].space}": {new_diff[index + offset - 1].text}',
                            f'"{new_diff[index + offset].space}": {new_diff[index + offset].text}',
                        )
                        offset += 1

                sequence_root = None
                sequence_indices = []

            if token.pos_ != sequence_root and cleaned not in LISTING_TERMINATORS:
                sequence_root = token.pos_
                sequence_indices = []
            else:
                sequence_indices.append(i)

    result = ""

    for token in new_diff:
        result += token.text + token.space

    return new_diff, result


def flag_simple_listings(diff, text, nlp):
    tokens = nlp(text)
    result_diff, result_text = insert_simple_listings(
        tokens, [t.text for t in tokens], diff
    )

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
