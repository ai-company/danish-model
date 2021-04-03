from . import explain

LISTING_TERMINATORS = ["og", "eller", "samt", "plus", "osv.", "m.fl.", "etc.", ""]


def clean_token_text(text):
    return text.replace(",", "").replace(".", "").replace(";", "").strip()


def insert_simple_listings(tokens, result=[], changes=None):
    alter_changes = changes is not None

    sequence_root = None
    sequence_indices = []

    for i, token in enumerate(tokens):
        if sequence_root is None:
            sequence_root = token.pos_
        else:
            cleaned = clean_token_text(token.text.lower())
            if sequence_root and cleaned in LISTING_TERMINATORS:
                for index in sequence_indices:
                    if alter_changes:
                        changes.insert(
                            index,
                            explain.change("add", ",", "Tilføj opremsningskomma."),
                        )
                    result.insert(index, ",")

                sequence_root = None
                sequence_indices = []

            if token.pos_ != sequence_root and cleaned not in LISTING_TERMINATORS:
                sequence_root = token.pos_
                sequence_indices = []
            else:
                sequence_indices.append(i)

    return result


def flag_simple_listings(tokens, changes):
    result = insert_simple_listings(tokens, [t.text for t in tokens], changes)

    foo = result.copy()

    result = " ".join(result).replace(", ,", ",").replace(" ,", ",")

    return result


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
            if i != len(tokens) and "inf" not in tokens[i + 1].morph.verb_form_:
                result.append(",")
        elif i != 0 and token.text == "men" and token.pos_ != "NOUN":
            result.append(",")

        result.append(token.text)

    result = insert_simple_listings(tokens, result)

    result = " ".join(result).replace(", ,", ",").replace(" ,", ",")

    return result
