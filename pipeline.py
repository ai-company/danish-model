from copy import copy
from pprint import pprint
from typing import List, final
from diff_token import DiffSpac, DiffToken, Lexeme, LexemeType, tokenize

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


def strip_user_commas(diff, text):
    new_text = text.replace(",", "")
    new_diff = tokenize(new_text)

    return new_diff, new_text


def collectChanges(diff_history, index) -> List[DiffToken]:
    if len(diff_history) < 1:
        return []

    changes = [diff_history[-1][index]]

    if type(diff_history[-1][index].index) is list:
        changes.append(
            list(
                map(
                    lambda i: collectChanges(diff_history[:-1], i),
                    diff_history[-1][index].index,
                )
            )
        )
    elif diff_history[-1][index].index is not None:
        changes.extend(collectChanges(diff_history[:-1], diff_history[-1][index].index))

    return changes


def process(text):
    """
    Processes a text. Gives back diff and better text.

    Params:
        - text: The input.

    Returns:
        - diff: What changed.
        - text: The output.
    """

    result = []

    for sentence in map(str, sentencize(text).sents):
        initial_diff = []
        diff_history = []

        diff = tokenize(sentence)
        diff_history.append(diff)
        initial_diff = diff
        pprint(text)
        pprint(diff)

        diff, text = spell(diff, text)
        diff_history.append(diff)
        pprint(text)
        pprint(diff)

        diff, text = strip_user_commas(diff, text)
        diff_history.append(diff)
        pprint(text)
        pprint(diff)

        diff, text = flag_simple_listings(diff, text, sent_nlp)
        diff_history.append(diff)
        pprint(text)
        pprint(diff)

        diff, text = compound_words(diff, text, sent_nlp)
        diff_history.append(diff)
        pprint(text)
        pprint(diff)

        diff, text = grammar(diff, text)
        diff_history.append(diff)
        pprint(text)
        pprint(diff)

        diff, text = commas(diff, text)
        diff_history.append(diff)
        pprint(text)
        pprint(diff)

        # pprint(diff_history)

        diff = []

        lastindex = -1

        for i in range(len(tokenize(text))):
            changelist = collectChanges(diff_history, i)

            change = None

            for item in changelist[::-1]:
                if item.index is None:  # addition
                    change = item.clone()
                    break

                elif type(item) is list:  # merge
                    # TODO: recursively collect changes for the origins too
                    if change is None:
                        change = item[0][-1].clone_clean()
                    origins = list(map(lambda c: c[-1].clone(), item))
                    change.origin = origins

                else:  # existing item
                    if change is None:
                        change = item.clone_clean()

                    change.lexeme = copy(item.lexeme)

                    if item.explanation:
                        change.explanation.extend(item.explanation)
                    if item.change_type != "none":
                        change.change_type = item.change_type
                    if item.change:
                        change.change = item.change

            if change.index == lastindex:  # split
                origin = changelist[-1].clone_clean()
                origin.explanation = ["Ordet bør opdeles i flere."]
                origin.change_type = "split"
                origin.change = [diff[-1], change]
                diff[-1] = origin
            else:
                diff.append(change)

            lastindex = changelist[-1].index

        # check removals
        diff_with_removals = []
        i = j = 0
        while i < len(initial_diff) and j < len(diff):
            if initial_diff[i].lexeme.type == diff[j].lexeme.type:
                if diff[j].change_type == "add":
                    diff_with_removals.append(initial_diff[i].clone_clean())
                else:
                    diff_with_removals.append(diff[j])
                i += 1
                j += 1

            else:
                if initial_diff[i].lexeme.type == LexemeType.PUNC:
                    # punctuation removal
                    removed = initial_diff[i].clone_clean()
                    removed.change_type = "remove"
                    removed.explanation.append("Der bør ikke være et komma her.")
                    diff_with_removals.append(removed)
                    i += 1
                elif diff[j].lexeme.type == LexemeType.PUNC:
                    # punctuation addition
                    diff_with_removals.append(diff[j])
                    j += 1
                else:
                    raise Exception("unreachable!")

        if j < len(diff):  # last punctuation
            diff_with_removals.append(diff[j])

        # extract spaces
        final_diff = []
        for change in diff_with_removals:
            if change.lexeme.space != "":
                final_diff.append(change.stripped())
                final_diff.append(DiffSpac(change.lexeme.space, None))
            else:
                final_diff.append(change.clone())

        pprint(final_diff)
        pprint(list(map(DiffToken.to_dict, final_diff)))

        result.extend(final_diff)

    return text, list(map(DiffToken.to_dict, result))
