def heuristics(tokens):
    """
    Heuristics for catching low-hanging fruits with 100% accuracy.

    Params:
        - tokens: A list of spaCy tokens for the most recent pass.

    Returns:
        - result: Text result.
    """
    result = []

    for i, token in enumerate(tokens):
        if token.text in ['der', 'som'] and token.dep_ == 'nsubj':
            result.append(',')
        elif token.text == 'at':
            if i != len(tokens) and 'inf' not in tokens[i + 1].morph.verb_form_:
                result.append(',')
        elif i != 0 and token.text == 'men' and token.pos_ != 'NOUN':
            result.append(',')

        result.append(token.text)

    result = ' '.join(result).replace(', ,', ',').replace(' ,', ',')

    return result
