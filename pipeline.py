from pprint import pprint
from diff_token import DiffToken, Lexeme, LexemeType, tokenize

import spacy

from comma.comma import init as comma_init
from comma.clauses import flag_simple_listings

from spell.spell import bake_spelling as spell_init

from spell.grammar import init as grammar_init
from spell.compound import compound_words

# from spell.util import parse_words_and_quotes, parse_words_all_original

from pysbd.utils import PySBDFactory

sent_nlp = spacy.load("da_core_news_lg")
sent_nlp.add_pipe(PySBDFactory(sent_nlp), first=True)

spell, unmasker = spell_init()
grammar = grammar_init(unmasker, sent_nlp)
commas = comma_init(sent_nlp)


def sentencize(text):
    return sent_nlp(text)


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
        pprint(text)

        diff, text = spell(diff, text)
        diff_history.append(diff)
        pprint(text)

        diff, text = flag_simple_listings(diff, text, sent_nlp)
        diff_history.append(diff)
        pprint(text)

        diff, text = compound_words(diff, text, sent_nlp)
        diff_history.append(diff)
        pprint(text)

        diff, text = grammar(diff, text)
        diff_history.append(diff)
        pprint(text)

        diff, text = commas(diff, text)
        diff_history.append(diff)
        pprint(text)

    pprint(diff_history)
    # return diff_history
