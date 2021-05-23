import spacy
import re

# from comma.comma import init
# from comma.clauses import flag_simple_listings

# from spell.spell import bake_spelling as spell_init
# from spell.grammar import init as grammar_init
# from spell.compound import compound_words
# from spell.util import parse_words_and_quotes, parse_words_all_original

from pysbd.utils import PySBDFactory

sent_nlp = spacy.load("da_core_news_lg")
sent_nlp.add_pipe(PySBDFactory(sent_nlp), first=True)


class Token:
    def __init__(self, text, capitalization_mask, type, index, explanation):
        self.text = text
        self.capitalization_mask = capitalization_mask
        self.type = type
        self.index = index
        self.explanation = explanation

    def __str__(self):
        return f'T<"{self.text}", {self.type} @ {self.index}>'


def sentencize(text):
    return sent_nlp(text)


def tokenize(phrase, split_space=False):
    return list(
        map(
            lambda x: Token(
                x[1].group(0),
                x[1].group(0),
                list(
                    {k: v for k, v in x[1].groupdict().items() if v is not None}.keys()
                )[0],
                x[0],
                [],
            ),
            enumerate(
                re.finditer(
                    r"(?P<number>[0-9]+[,\.][0-9]+|[0-9]+)|(?P<word>\w+)|(?P<space>\t|\n|\s+)|(?P<punctuation>\W)",
                    phrase,
                )
            ),
        )
    )


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
    diff = tokenize(text)

    import pdb

    pdb.set_trace()

    return

    for sentence in sentencize(text):
        diff, text = spell(diff, text)
        diff_history.append(diff)

        diff, text = flag_simple_listings(diff, text)
        diff_history.append(diff)

        diff, text = compound_words(diff, text)
        diff_history.append(diff)

        diff, text = grammar(diff, text)
        diff_history.append(diff)

        diff, text = commas(diff, text)
        diff_history.append(diff)
