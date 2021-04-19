from os.path import join, dirname

corpus_words = dict()

BINDINGS = ["s", "e", "n", ""]

with open(join(dirname(__file__), "dictionary.txt"), "r") as f:
    for line in f:
        corpus_words[line.split()[0]] = True


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
        print(word)
        return True
    else:
        for i in range(len(word), -1, -1):
            buffer = word[i : len(word)]

            flag = False

            if buffer in corpus_words:
                flag = True
            elif buffer != "" and buffer[-1] in BINDINGS:
                flag = buffer[:-1] in corpus_words

            if flag:
                if is_deep_real(word[: len(word) - len(buffer)]):
                    if len(buffer) + (len(word) - len(buffer)) == len(word):
                        return True

    return False


if __name__ == "__main__":
    while True:
        test = input("> ")
        print(is_deep_real(test))