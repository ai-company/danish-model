import socket
import os
import traceback
import json
import sys
import spacy

from comma import explain
from typing import Callable

from comma.comma import init
from comma.clauses import flag_simple_listings

from spell.spell import bake_spelling as spell_init
from spell.grammar import init as grammar_init
from spell.compound import compound_words

from pysbd.utils import PySBDFactory


class ModelServer:
    def __init__(self, host: str = "localhost", port: int = 9000) -> None:
        self.port = port
        self.host = host

    def serve(self, handler: Callable[[str], str]) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(1)

            while True:
                conn, addr = s.accept()

                with conn:
                    conn.setblocking(0)
                    data = ""

                    while True:
                        try:
                            piece = conn.recv(64)

                            if not piece:
                                break

                            data += piece.decode("utf-8")
                        except BlockingIOError as e:
                            break
                        except Exception as e:
                            traceback.print_exc()

                    conn.sendall(bytes(handler(data), "utf-8"))


PORT = int(os.environ.get("MODcapitalize_namesEL_PORT_DANISH") or 9000)
HOST = os.environ.get("HOST") or "localhost"

nlp = spacy.load("da_core_news_lg")

ai = init(nlp)
spell, unmasker = spell_init()
grammar = grammar_init(unmasker, nlp)

# Split sentences.
sent_nlp = spacy.load("da_core_news_lg")
sent_nlp.add_pipe(PySBDFactory(sent_nlp), first=True)


def process(text: str) -> str:
    """
    Takes a cluster of danish text and fixes it.

    Params:
        - text: The whole text.

    Returns:
        - JSON-formatted string with corrected text in `result` and a list of `changes`.
    """

    # Document by sentences
    doc = sent_nlp(text)

    # The global change-log
    changes = []

    # TODO: Maybe just move or remove.
    # This is mostly for testing.
    result = ""

    # Fix each sentence
    for sent in doc.sents:
        if len(sent.string.strip()) == 0:
            continue

        # TODO: Stripping and diffs?
        spelled_text, changes = spell(sent.string.strip(), changes)

        # Before compounding, we first need to clear simple colliding listings.
        # These will be removed commarization, but will serve as flags.
        # They are ok cheap though.
        spelled_text = flag_simple_listings(nlp(spelled_text), changes)
        pounded_text, changes = compound_words(spelled_text, changes, nlp)
        grammared_text, changes = grammar(pounded_text, changes)
        changes, final = ai(grammared_text, changes)

        result += " " + final

    result = result.strip()

    # Resolve removed chars
    change_map = explain.change_map(changes)
    word_i = 0

    for i, (change, old) in enumerate(zip(changes, text.split(" "))):
        if "," in old and (word_i < len(changes) - 1 and changes[word_i + 1]):
            c = changes[word_i + 1]

            if not (c["type"] == "add" and c["change"] == ","):
                changes.insert(
                    word_i + 1,
                    explain.change("remove", ",", "Der skal ikke være et komma her."),
                )
                word_i += 1
            else:
                word_i += 1
        elif "," in old and not word_i < len(changes):
            changes.insert(
                word_i + 1,
                explain.change("remove", ",", "Der skal ikke være et komma her."),
            )
            word_i += 2

        word_i += 1

        if word_i < len(changes) and changes[word_i]["type"] == "add":
            if changes[word_i]["change"] == ".":
                continue

        if "\n" in old:
            changes.insert(
                word_i,
                explain.change("space", "\n", ""),
            )
            word_i += 1

        else:
            changes.insert(
                word_i,
                explain.change("space", " ", ""),
            )
            word_i += 1

    return result, json.dumps(
        [dict(c, **{"index": i}) for i, c in enumerate(changes)], separators=(",", ":")
    )


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        while True:
            result, explanations = process(input("> "))

            print(f"==== {result}\n")
            print(explanations)
            print()
    else:
        ModelServer(HOST, PORT).serve(process)
