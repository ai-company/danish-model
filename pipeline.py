from diff_token import DiffToken

import spacy
import re

# from comma.comma import init
from comma.clauses import flag_simple_listings

# from spell.spell import bake_spelling as spell_init

# from spell.grammar import init as grammar_init
# from spell.compound import compound_words
# from spell.util import parse_words_and_quotes, parse_words_all_original

from pysbd.utils import PySBDFactory

sent_nlp = spacy.load("da_core_news_lg")
sent_nlp.add_pipe(PySBDFactory(sent_nlp), first=True)


def sentencize(text):
    return sent_nlp(text)


def tokenize(phrase, split_space=False):
    tokens = []
    for i, token in enumerate(
        re.finditer(
            r"(?P<number>[0-9]+([,.][0-9]+)*)|(?P<word>\w+)|(?P<space>\t|\n|\s+)|(?P<punctuation>\W)",
            phrase,
        )
    ):
        type = list(
            {k: v for k, v in token.groupdict().items() if v is not None}.keys()
        )[0]

        if type == "space":
            tokens[-1].space = token.group(0)
        else:
            tokens.append(
                DiffToken(
                    token.group(0),
                    token.group(0),
                    type,
                    i,
                    [],
                )
            )

    for i, token in enumerate(tokens):
        token.index = i

    return tokens


def process(text):
    """
    Processes a text. Gives back diff and better text.

    Params:
        - text: The input.

    Returns:
        - diff: What changed.
        - text: The output.
    """

    diff_history = []

    for sentence in map(str, sentencize(text).sents):
        diff = tokenize(sentence)
        diff_history.append(diff)

        # diff, text = spell(diff, text)
        # diff_history.append(diff)

        diff, text = flag_simple_listings(diff, text, sent_nlp)
        diff_history.append(diff)

        import pdb

        pdb.set_trace()

        # diff, text = compound_words(diff, text)
        # diff_history.append(diff)

        # diff, text = grammar(diff, text)
        # diff_history.append(diff)

        # diff, text = commas(diff, text)
        # diff_history.append(diff)

    return diff_history
