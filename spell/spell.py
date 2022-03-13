from copy import copy, deepcopy
from pprint import pprint
from sys import executable
from typing import List
from diff_token import DiffToken, LexemeType, tokenize
from transformers import pipeline, AutoTokenizer, AutoModelForPreTraining

from .prob_spell import init
from nltk.corpus import words as corpus_words
from grammar.grammar import NAMES

from . import explain
from . import util
from os.path import join, dirname

BINDINGS = ["s", "e", "n", ""]

corpus_words = dict()

with open(join(dirname(__file__), "data/dictionary.txt"), "r") as f:
    for line in f:
        corpus_words[line.split()[0]] = True

corpus_words = {**corpus_words, **{k.capitalize(): v for k, v in NAMES.items()}}

tokenizer = AutoTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
unmasker = pipeline("fill-mask", model="Maltehb/danish-bert-botxo", tokenizer=tokenizer)
prob_spell = init()

# TODO: Move to CSV :)
letter_mix_map = (
    ("rd", "r"),
    ("tt", "t"),
    ("t", "tt"),
    ("n", "nd"),
    ("nd", "n"),
    ("l", "ll"),
    ("k", "g"),
    ("g", "k"),
    ("n", "m"),
    ("s", "c"),
    ("z", "s"),
    ("s", "z"),
    ("æ", "e"),
    ("e", "æ"),
    ("j", "g"),
    ("øv", "eu"),
    ("g", "j"),
    ("d", "t"),
    ("t", "d"),
    ("o", "u"),
    ("o", "ø"),
    ("u", "o"),
    ("t", "ss"),
    ("f", "ph"),
    ("ti", "j"),
    ("v", "hv"),
    ("hv", "v"),
    ("nn", "nd"),
    ("ll", "ld"),
    ("kk", "gg"),
    ("in", "ind"),
    ("u", "in"),
    ("ø", "eu"),
    ("eu", "ø"),
    ("ti", "si"),
    ("sj", "ti"),
    ("sj", "si"),
)

common_spelling_mistakes = dict()


def is_deep_real(word: str) -> bool:
    """
    Deep run of possible compounds.

    Params:
        - word: The word that needs to be verified.

    Returns:
        - result: Whether the word is okay.
    """

    length = len(word)

    if word in corpus_words:
        return True
    else:
        for i in range(len(word), -1, -1):
            #
            buffer = word[i : len(word)]

            flag = False

            if buffer in corpus_words:
                flag = True
            elif buffer[-1] in BINDINGS:
                flag = buffer[:-1] in corpus_words

            if flag:
                if is_deep_real(word[: len(word) - largest]):
                    if largest + len(word) - largest:
                        return True

    return False


def is_real(word):
    return word in corpus_words


def low_hanging_fruits(sentence, nlp):
    words = util.parse_words(sentence, nlp=nlp)

    for i, word in enumerate(words):
        if i < len(words) - 2 and len(words) > 1:
            bigram = f"{word} {words[i + 1]}"

            if result := common_spelling_mistakes.get(bigram):
                words[i] = result
                del words[i + 1]

        if result := common_spelling_mistakes.get(word):
            words[i] = result

    return " ".join(words)


def fix_typo(word):
    if not is_real(word):
        if len(word) > 1:
            if word[0] == word[1] and is_real(word[1:]):
                return word[1:]

            if word[-1] == word[-2] and is_real(word[:-1]):
                return word[:-1]

        maybes = []

        for i, letter in enumerate(word):
            for (key, c) in letter_mix_map:
                if key == letter:
                    maybe = word[:i] + c + word[i + 1 :]

                    if is_real(maybe):
                        maybes.append(maybe)

                if len(word) > 1:
                    if key == word[i - 1] + letter:
                        maybe = word[: i - 1] + c + word[i + 1 :]

                        if is_real(maybe):
                            maybes.append(maybe)

        best_score = 0
        best_maybe = word

        for maybe in maybes:
            best_maybe = maybe

        return best_maybe

    return word


def explain_none(changes, i, change, explain):
    changes[i]["type"] = "replace"
    changes[i]["change"] = changes[i]["origin"]
    changes[i]["origin"] = change
    changes[i]["explain"] = explain if type(explain) is list else [explain]


def init():
    # TODO: words replaced with punctuation, that's pretty fucked
    def fix(diff: List[DiffToken] = [], text="", nlp=None):
        """
        Fixes incorrect spelling and grammatically incorrect sequences.

        Params:
            - text: The text to be fixed.

        Returns:
            - result: The fixed text.
            - diff: An incremental changelog of what and how.
        """

        # TODO: Cache things.
        # text = text.replace(",", "").replace(" - ", " ")

        unks = []
        words = []
        change_cache = {}

        for i, word in enumerate(util.parse_words(text, nlp=nlp)):
            fixed = fix_typo(word)
            words.append(fixed)

            if fixed != word:
                change_cache[i] = (word, "Dette var nok en tastefejl.")

        sentence = " ".join(words)
        sentence = low_hanging_fruits(sentence, nlp)

        computed, changes = prob_spell(
            sentence,
            [
                t[0].isupper() and not i == 0
                for i, t in enumerate(util.parse_words(text, nlp=nlp, lower=False))
            ],
            nlp,
            corpus_words,
        )

        masks = {}

        # TODO: This will change.
        words = list(
            filter(
                lambda x: len(
                    x.replace("-", "")
                    .replace(",", "")
                    .replace("(", "")
                    .replace(")", "")
                )
                != 0,
                words,
            )
        )

        # for i, word in enumerate(words):
        #    if word not in corpus_words and len(word) > 0:
        #        unks.append(word)
        #        words[i] = word

        # We need a somewhat fixed version for the language model to suggest.
        #        mask = computed.copy()[0].term.split()

        #        old = mask[i]

        #        mask[i] = "[MASK]"
        #        masks[i] = (word, mask, old)

        for i, change in change_cache.items():
            # This will always be none. The word was fixed before. :)
            old = changes[i]

            # The following will transform none-object into corresponding chonge.
            # Note: the origin will have been the change made before correction pass.
            explain_none(changes, i, change[0], change[1])

        computed_text = computed[0].term

        # pprint(changes)
        # pprint(computed_text)

        # Yea, I know. Nvm, what did I know??
        # TODO: should not split on space and instead properly parse?
        # TODO: this ruins splits on occasion
        # TODO: handle multiple masks!!!
        # result = []
        # for i, word in enumerate(computed_text.split(" ")):
        #     if mask := masks.get(i):
        #         tokens = [x["token_str"] for x in unmasker(" ".join(mask[1]))]
        #         pprint(changes[i])
        #         pprint(tokens)
        #         pprint(masks)

        #         found_match = False

        #         for token in tokens:
        #             if (
        #                 mask[0] in token
        #                 or token in mask[0]
        #                 and mask[2] not in corpus_words
        #             ):
        #                 if changes[i]["type"] == "none":
        #                     explain_none(
        #                         changes, i, token, "Indsættelse af korrekt ord."
        #                     )
        #                 else:
        #                     changes[i]["change"] = token
        #                     changes[i]["explain"] = ["Indsættelse af korrekt ord."]

        #                 result.append(token)
        #                 found_match = True
        #                 break

        #         if not found_match:
        #             result.append(word)

        #     else:
        #         result.append(word)

        # reconcile diffs -------------------------------------

        # pprint(changes)

        # TODO: this fixes missing punctuation, clean up when punctuation is fixed above
        # pprint(list(map(DiffToken.from_dict, changes)))

        changes = list(
            filter(
                lambda t: t.lexeme.type == LexemeType.WORD,
                map(DiffToken.from_dict, changes),
            )
        )
        new_changes: List[DiffToken] = []

        # print("FUUUUUUUUCK!!")
        # pprint(changes)

        last_was_merge = False

        for i, item in enumerate(diff):

            if last_was_merge:
                last_was_merge = False
                continue

            if item.lexeme.type != LexemeType.WORD:
                new_changes.append(item)
            elif changes[0].change_type == "merge":
                change = changes.pop(0)

                change.origin = [str(diff[i].lexeme), str(diff[i + 1].lexeme)]
                change.lexeme.space = diff[i + 1].lexeme.space
                change.index = [i, i + 1]

                new_changes.append(change)

                last_was_merge = True
            elif len(changes) > 0:
                change = changes.pop(0)
                change.lexeme.space = item.lexeme.space
                change.origin = str(item.lexeme)

                new_changes.append(change)
            else:
                pprint(changes)
                pprint(
                    list(
                        filter(
                            lambda t: t.lexeme.type == LexemeType.WORD,
                            diff,
                        )
                    )
                )

                raise Exception("unreachable!")

        changes = new_changes
        new_changes = []

        j = 0
        offset = 0
        while j < len(changes):
            if changes[j].change_type == "split":
                for si, change in enumerate(changes[j].change):
                    change = change.clone()
                    change.index = j + offset

                    cap_mask = (
                        diff[j].lexeme.text[: len(change.lexeme.text)]
                        if si == 0
                        else diff[j].lexeme.text[len(change.lexeme.text) :]
                    )

                    change.lexeme.text = util.match_capitalization(
                        change.lexeme.text, cap_mask
                    )
                    change.change = str(change.lexeme)
                    new_changes.append(change)

                new_changes[-1].lexeme.space = changes[j].lexeme.space

            else:
                change = changes[j].clone()

                change.lexeme.space = diff[j].lexeme.space
                change.lexeme.text = util.match_capitalization(
                    change.lexeme.text, diff[j].lexeme.text
                )
                if change.change is not None:
                    change.change = str(change.lexeme)
                change.index = j + offset
                if changes[j].change_type == "merge":
                    offset += 1
                    change.index = [change.index, change.index + 1]
                new_changes.append(change)

            j += 1

        return new_changes, "".join(map(str, new_changes))

    return fix, unmasker


if __name__ == "__main__":
    while True:
        text = input("> ")
        fix = bake_spelling()

        if text == "@open":
            with open("test_en.txt", "r") as f, open("out.txt", "w+") as out:
                for line in f:
                    out.write(f"{fix(line)}\n")

        print(fix(text))
