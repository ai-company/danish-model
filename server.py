from traceback_with_variables import activate_by_import, prints_exc

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
from spell.util import parse_words_and_quotes, parse_words_all_original

from pysbd.utils import PySBDFactory


class ModelServer:
    def __init__(self, host: str = "localhost", port: int = 9000) -> None:
        self.port = port
        self.host = host

    def serve(self, handler: Callable[[str], str]) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(1)

            while True:
                conn, addr = s.accept()

                with conn:
                    conn.setblocking(0)
                    data = b""

                    while True:
                        try:
                            piece = conn.recv(64)

                            if not piece:
                                break

                            data += piece
                        except BlockingIOError as e:
                            break
                        except Exception as e:
                            traceback.print_exc()

                    conn.sendall(
                        bytes(handler(data.decode("utf-8", "ignore")), "utf-8")
                    )


PORT = int(os.environ.get("MODEL_PORT_DANISH") or 9000)
HOST = os.environ.get("HOST") or "localhost"

nlp = spacy.load("da_core_news_lg")

ai = init(nlp)
spell, unmasker = spell_init()
grammar = grammar_init(unmasker, nlp)

# Split sentences.
sent_nlp = spacy.load("da_core_news_lg")
sent_nlp.add_pipe(PySBDFactory(sent_nlp), first=True)


def cache(c: str, text: str) -> dict:
    result = dict()

    for i, token in enumerate(parse_words_and_quotes(text)):
        if token == '"':
            result[i] = True

    return result


def is_nospace(change) -> bool:
    return (
        (change["type"] == "none" and change["origin"] in ",.")
        or (change["type"] == "replace" and change["change"] in ",.")
        or (change["type"] == "add" and change["change"] in ",.")
    )


def no_spaces(a):
    return a["type"] != "space"


@prints_exc
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
        sent_changes = []
        sent_text = sent.string.strip()

        if len(sent_text) == 0:
            continue

        quote_map = cache('"', sent_text)

        # TODO: Stripping and diffs?
        spelled_text, sent_changes = spell(sent_text, sent_changes)

        # Before compounding, we first need to clear simple colliding listings.
        # These will be removed commarization, but will serve as flags.
        # They are ok cheap though.
        spelled_text = flag_simple_listings(nlp(spelled_text), sent_changes)

        pounded_text, sent_changes = compound_words(spelled_text, sent_changes, nlp)
        grammared_text, sent_changes = grammar(pounded_text, sent_changes)

        for k in quote_map.keys():
            sent_changes.insert(
                k,
                explain.change("none", '"'),
            )

        sent_changes, final = ai(grammared_text, sent_changes)

        final = final.replace(",,", ",").replace(
            ", ,", ","
        )  # TODO: Look at this (with eyes)

        if len(sent_changes) > 0 and (
            sent_changes[-1]["type"] == "add"
            and sent_changes[-1]["change"] == "."
            and text.strip()[-1] == "."
        ):
            sent_changes[-1] = explain.explain("none", ".")

        result += " " + final
        changes += sent_changes

    result = (
        result.strip()
        .replace("( ", "(")
        .replace(" )", ")")
        .replace(" ?", "?")
        .replace(" !", "!")
    )

    # Resolve removed chars
    change_map = explain.change_map(changes)

    word_i = 0
    last = ""
    changes_cache = [*changes]  # TODO: Think of something smart.

    last_add = False
    just_removed = False

    old_text_parts = parse_words_all_original(text)

    for i, (change, old) in enumerate(zip(changes_cache, old_text_parts)):
        just_removed = False

        c1 = changes[i + word_i]

        if c1["type"] == "add" and c1["change"] == ",":
            if changes[i + word_i]["type"] == "space":
                del changes[i + word_i]
                word_i -= 1

        c = changes[i + word_i]

        if "," in old:
            if not (c["type"] == "add" and c["change"] == ","):
                abort_mission = False
                if c["type"] == "split":
                    for change in c["change"]:
                        if change["type"] == "add":
                            abort_mission = True

                if not abort_mission:
                    changes.insert(
                        i + word_i,
                        explain.change(
                            "remove", "", "Der skal ikke være et komma her.", ","
                        ),
                    )

                    word_i += 1

                    changes.insert(
                        i + word_i,
                        explain.change("space", " ", ""),
                    )

                    continue

                    just_removed = True

        elif "," in old:
            if not (word_i > 0 and changes[word_i]["type"] != "add"):

                changes.insert(
                    i + word_i,
                    explain.change(
                        "remove", "", "Der skal ikke være et komma her.", ","
                    ),
                )

                word_i += 1

                changes.insert(
                    i + word_i,
                    explain.change("space", " ", ""),
                )

                continue

                just_removed = True

        if change["type"] == "add" and change["change"] == ",":
            last_add = True

    word_i = 0
    changes_cache = [*changes]  # TODO: Think of something smart. #2

    for i, change in enumerate(changes_cache):
        c1 = changes[i + word_i]

        if i + word_i < len(changes):
            if is_nospace(changes[i + word_i]):
                last = "origin" in change and change["origin"] or change["change"]
                continue

        if last not in "([{" and not (c1["type"] == "add" and "," in c1["change"]):
            if (
                changes[i + word_i - 1]["type"] == "remove"
                or changes[i + word_i - 1]["type"] == "space"
            ):
                last = "origin" in change and change["origin"] or change["change"]
                continue

            if "\n" in old:
                changes.insert(
                    i + word_i,
                    explain.change("space", "\n", ""),
                )
                word_i += 1
            else:
                changes.insert(
                    i + word_i,
                    explain.change("space", " ", ""),
                )
                word_i += 1

        last = "origin" in change and change["origin"] or change["change"]

        if type(last) == list:
            last = last[-1]

    old_offset = 0

    for i, change in enumerate(changes):
        if i - old_offset < len(old_text_parts):
            old = old_text_parts[i - old_offset]

            if change["type"] == "space":
                old_offset += 1

            if (
                change["type"] == "replace"
                and "begyndelsesbogstav" in change["explain"]
            ) and old[0].lower() != old[0]:
                changes[i] = explain.explain("none", change["change"])

            if change["type"] == "add" and change["change"] == "," and old == ",":
                change[i] = explain.explain("none", ",")

    return result, json.dumps(
        [dict(c, **{"index": i}) for i, c in enumerate(changes)], separators=(",", ":")
    )


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        while True:
            explanations = process(input("> "))

            print(explanations)
            print()
    else:

        def _process(text: str):
            _, changes = process(text)
            return changes

        ModelServer(HOST, PORT).serve(_process)
