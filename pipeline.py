import spacy
import pysbd

from os.path import dirname, join
from pprint import pprint
from copy import copy
from typing import List, final
from inspect import signature

from comma import comma
from comma.clauses import flag_simple_listings

from spell import spell
from grammar import grammar
from spell.compound import compound_words

from diff_token import DiffSpac, DiffToken, Lexeme, LexemeType, tokenize
from itertools import takewhile

nlp = spacy.load("da_core_news_lg")
seg = pysbd.Segmenter(language="da", clean=False)

spell, unmasker = spell.init()
grammar, grammar_second_pass = grammar.init(unmasker, nlp)
commas = comma.init(nlp)


def sentencize(text):
    proposal = seg.segment(text)
    result = []

    accum = []

    for segment in proposal:
        if segment[-1] not in ":?!.":
            accum.append(segment)
        else:
            result.append(" ".join(accum + [segment]))

            accum = []

    return result + ([" ".join(accum)] or [])


def strip_user_commas(diff, text):
    # new_text = text.replace(",", "")
    tokens = DiffToken.from_spacy_list(nlp(text))

    # filter commas
    new_diff = []
    for i, token in enumerate(tokens):
        if token.lexeme.text == ",":
            # filter comma but keep space
            if len(new_diff) > 0:
                new_diff[-1].lexeme.space = (
                    token.lexeme.space if token.lexeme.space != "" else " "
                )
        else:
            new_diff.append(token)

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
            else:
                pprint(diff)
                pprint(new_diff)
                print(f"{i} '{diff[i]}' {j} '{new_diff[j]}'")
                raise Exception("unreachable!")

    return new_diff, "".join(map(str, new_diff))


def collect_changes(diff_history, index) -> List[DiffToken]:
    if len(diff_history) < 1:
        return []

    changes = [diff_history[-1][index]]

    if type(diff_history[-1][index].index) is list:
        changes.append(
            list(
                map(
                    lambda i: collect_changes(diff_history[:-1], i),
                    diff_history[-1][index].index,
                )
            )
        )
    elif diff_history[-1][index].index is not None:
        changes.extend(
            collect_changes(diff_history[:-1], diff_history[-1][index].index)
        )

    return changes


def process(text, debug=False):
    result_diff: List[DiffToken] = []
    result_text = ""
    text += "\n"  # i don't know what this fixes, but having an extra newline prevents off-by-one crash in commarizer

    for segment in sentencize(text):
        sentence = nlp(segment)

        initial_diff = []
        diff_history = []

        text = str(sentence)
        diff = DiffToken.from_spacy_list(sentence)

        diff_history.append(diff)

        initial_diff = diff

        if debug:
            print("tokenize: ")
            pprint(text)
            pprint(diff)

        # Keeping it short:
        # - function to apply, whether it should be served the NLP.
        for func, pass_nlp in [
            (spell, True),
            (strip_user_commas, False),
            (flag_simple_listings, True),
            (compound_words, True),
            (grammar, False),  # Already has it. :)
            (commas, False),  # Ditto.
            (grammar_second_pass, False),
        ]:
            args = [diff, text, nlp][: len(signature(func).parameters)]

            diff, text = func(*args)
            diff_history.append(diff)

            if debug:
                print(f"{func.__name__}: ")
                pprint(text)
                pprint(diff)

        if debug:
            print("\n--- final diffs ---\n")

        reconciled_diff: List[DiffToken] = []

        lastindex = -1

        # pprint(DiffToken.from_spacy_list(sent_nlp(text)))
        for i in range(len(diff)):
            changelist = collect_changes(diff_history, i)
            change = None
            split_merge_case = False

            for item in changelist[::-1]:
                if item.index is None:  # addition
                    change = item.clone()
                    break

                elif type(item) is list:  # merge
                    # TODO: recursively collect changes for the origins too
                    if change is None:
                        change = item[0][-1].clone_clean()

                    # TODO: mark which origin the explanation belongs to
                    # collect explanations from each origin branch
                    explanations = []

                    for origin in item:
                        for change in origin:
                            if type(change.explanation) is list:
                                explanations.extend(change.explanation)
                            else:
                                explanations.append(change.explanation)

                    _before = change.explanation
                    change.explanation = explanations

                    # double check if merge didn't originate from a previous split
                    change.origin = []
                    for origin in item:
                        # object ref comparison here
                        if len(change.origin) == 0 or (
                            len(change.origin) > 0 and change.origin[-1] != origin[-1]
                        ):
                            change.origin.append(origin[-1])

                    change.origin = list(map(str, change.origin))

                    # merge originating from a previous split
                    if len(change.origin) == 1:
                        change.origin = change.origin[0]
                        split_merge_case = True

                else:  # existing item
                    if change is None:
                        change = item.clone_clean()
                        change.origin = str(change.lexeme)

                    change.lexeme = copy(item.lexeme)

                    if item.explanation and not split_merge_case:
                        if not change.explanation == item.explanation:
                            change.explanation.extend(item.explanation)

                    if item.change_type != "none":
                        if split_merge_case:
                            change.change_type = "none"
                        else:
                            change.change_type = item.change_type

                    if item.change:
                        change.change = item.change

                    if split_merge_case:
                        split_merge_case = False

            if change.index == lastindex:  # split
                splits = []

                while True:
                    splits.insert(0, reconciled_diff.pop())

                    if (
                        len(reconciled_diff) == 0
                        or reconciled_diff[-1].index != lastindex
                    ):
                        break
                splits.append(change)

                origin = changelist[-1].clone_clean()
                origin.explanation = ["Ordet bør opdeles i flere."]
                origin.change_type = "split"
                origin.change = splits

                reconciled_diff.append(origin)
            else:
                reconciled_diff.append(change)

            if changelist[-1].index is not None:
                lastindex = changelist[-1].index

        if debug:
            print("\n--- reconciled:")
            pprint(reconciled_diff)

        # check removals ----------------------------------

        diff_with_removals: List[DiffToken] = []
        i = j = 0
        while i < len(initial_diff) and j < len(reconciled_diff):
            old = initial_diff[i]
            new = reconciled_diff[j]

            if old.lexeme.type == new.lexeme.type and (
                (
                    old.lexeme.type == LexemeType.PUNC
                    and old.lexeme.text == new.lexeme.text
                )
                or (old.lexeme.type != LexemeType.PUNC)
            ):
                # print(f"match: '{old}' '{new}' ")
                if new.change_type == "add":
                    diff_with_removals.append(old)
                else:
                    diff_with_removals.append(new)

                if new.change_type == "merge":
                    i += 1

                i += 1
                j += 1

            else:
                if old.lexeme.type == LexemeType.PUNC and old.lexeme.text == ",":
                    # punctuation removal
                    # print(f"remove: '{old}' '{new}' ")
                    removed = old.clone_clean()
                    removed.change_type = "remove"
                    removed.change = ""
                    removed.explanation.append("Der bør ikke være et komma her.")
                    diff_with_removals.append(removed)
                    i += 1
                elif new.lexeme.type == LexemeType.PUNC and new.lexeme.text in (
                    ",",
                    ".",
                ):
                    # punctuation addition
                    # print(f"add: '{old}' '{new}' ")
                    diff_with_removals.append(new)
                    j += 1
                else:
                    pprint(initial_diff)
                    pprint(reconciled_diff)
                    print(i, old, j, new)
                    raise Exception("unreachable!")

        if j < len(reconciled_diff):  # last punctuation
            diff_with_removals.append(reconciled_diff[j])

        if debug:
            print("\n--- with removals:")
            pprint(diff_with_removals)

        # extract spaces ----------------------------------

        spaced_diff: List[DiffToken] = []
        for change in diff_with_removals:
            if change.change_type == "space":
                spaced_diff.append(change)
            elif change.change_type == "remove":
                if len(spaced_diff) > 0 and spaced_diff[-1].change_type == "space":
                    spaced_diff.insert(-1, change.stripped())
                else:
                    spaced_diff.append(change.stripped())
                    spaced_diff.append(DiffSpac(change.lexeme.space, None))
            elif change.lexeme.space != "":
                spaced_diff.append(change.stripped())
                spaced_diff.append(DiffSpac(change.lexeme.space, None))
            else:
                spaced_diff.append(change.stripped())

        if debug:
            print("\n--- spaced:")
            pprint(list(map(DiffToken.to_dict, spaced_diff)))

        # unset change if change == origin --------------------

        for change in spaced_diff:
            if change.origin == change.change:
                change.change = None

        # final -----------------------------------------------

        if debug:
            print("\n--- final:")
            pprint(list(map(DiffToken.to_dict, spaced_diff)))

        result_diff.extend(spaced_diff)
        result_text += text

    return result_text, list(map(DiffToken.to_dict, result_diff))


if __name__ == "__main__":
    import os

    debug = os.getenv("debug", "") == "true"

    while True:
        text = ""
        while True:
            try:
                text += input("CTRL+D to stop input > ") + "\n"
            except EOFError:
                break

        a, b = process(text, debug)

        print(a)
        print(b)
        print()
