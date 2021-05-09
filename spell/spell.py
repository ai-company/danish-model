from transformers import pipeline, AutoTokenizer, AutoModelForPreTraining

from .prob_spell import init
from nltk.corpus import words as corpus_words

from . import explain
from . import util
from os.path import join, dirname

BINDINGS = ["s", "e", "n", ""]

corpus_words = dict()

with open(join(dirname(__file__), "dictionary.txt"), "r") as f:
    for line in f:
        corpus_words[line.split()[0]] = True

tokenizer = AutoTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
unmasker = pipeline("fill-mask", model="Maltehb/danish-bert-botxo", tokenizer=tokenizer)
prob_spell = init()

# TODO: Move to CSV :)
letter_mix_map = {
    "rd": "r",
    "tt": "t",
    "t": "tt",
    "n": "nd",
    "nd": "n",
    "l": "ll",
    "k": "g",
    "g": "k",
    "n": "m",
    "s": "c",
    "z": "s",
    "s": "z",
    "æ": "e",
    "e": "æ",
    "j": "g",
    "øv": "eu",
    "g": "j",
    "d": "t",
    "t": "d",
    "o": "u",
    "u": "o",
    "t": "ss",
    "f": "ph",
    "ti": "j",
    "v": "hv",
    "hv": "v",
    "nn": "nd",
    "ll": "ld",
    "kk": "gg",
    "in": "ind",
    "u": "in",
    "ø": "eu",
    "eu": "ø",
    "ti": "si",
    "sj": "ti",
    "sj": "si",
}

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


def low_hanging_fruits(sentence):
    words = util.parse_words(sentence)

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

        for i, letter in enumerate(word):
            if c := letter_mix_map.get(letter):

                maybe = word[:i] + c + word[i + 1 :]

                if is_real(maybe):
                    return maybe

            if len(word) > 1:
                if c := letter_mix_map.get(word[i - 1] + letter):
                    maybe = word[: i - 1] + c + word[i + 1 :]

                    if is_real(maybe):
                        return maybe

    return word


def explain_none(changes, i, change, explain):
    changes[i]["type"] = "replace"
    changes[i]["change"] = changes[i]["origin"]
    print("WHAT", change)
    changes[i]["origin"] = change
    changes[i]["explain"] = explain


def bake_spelling():
    def fix(text, changes=[]):
        """
        Fixes incorrect spelling and grammatically incorrect sequences.

        Params:
            - text: The text to be fixed.

        Returns:
            - result: The fixed text.
            - changes: An incremental changelog of what and how.
        """

        # TODO: Cache things.
        text = text.replace(",", "").replace(".", "").replace(" - ", " ")

        words = list(map(fix_typo, util.parse_words(text)))
        unks = []
        words = []
        change_cache = {}

        for i, word in enumerate(util.parse_words(text)):
            fixed = fix_typo(word)
            words.append(fixed)

            if fixed != word:
                change_cache[i] = (word, "Dette var nok en tastefejl.")

        sentence = " ".join(words)
        sentence = low_hanging_fruits(sentence)

        computed, changes = prob_spell(sentence)

        masks = {}

        change_map = explain.change_map(changes)

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

        for i, word in enumerate(words):
            if word not in corpus_words and len(word) > 0:
                unks.append(word)
                words[i] = word

                # We need a somewhat fixed version for the language model to suggest.
                mask = computed.copy()[0].term.split()

                old = mask[i]
                mask[i] = "[MASK]"
                masks[i] = (word, mask, old)

        for i, change in change_cache.items():
            # This will always be none. The word was fixed before. :)
            old = changes[i]

            # The following will transform none-object into corresponding chonge.
            # Note: the origin will have been the change made before correction pass.
            explain_none(changes, i, change[0], change[1])

        computed_text = computed[0].term

        result = []

        # Yea, I know. Nvm, what did I know??
        for i, word in enumerate(computed_text.split(" ")):
            if mask := masks.get(i):
                tokens = [x["token_str"] for x in unmasker(" ".join(mask[1]))]

                found_match = False

                for token in tokens:
                    if (
                        mask[0] in token
                        or token in mask[0]
                        and mask[2] not in corpus_words
                    ):

                        if changes[i]["type"] == "none":
                            explain_none(
                                changes, i, token, "Indsættelse af korrekt ord."
                            )
                        else:
                            changes[i]["change"] = token
                            changes[i]["explain"] = "Indsættelse af korrekt ord."

                        result.append(token)
                        found_match = True
                        break

                if not found_match:
                    result.append(word)

            else:
                result.append(word)

        return " ".join(result), changes

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
