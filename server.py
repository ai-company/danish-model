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
    return (change["type"] == "none" and change["origin"] in ",.") or (
        change["type"] == "replace" and change["change"] in ",."
    )


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

    for i, (change, old) in enumerate(
        zip(changes_cache, parse_words_all_original(text))
    ):
        just_removed = False

        # OWNERSHIP CHECK
        if (
            change["type"] == "replace" and "begyndelsesbogstav" in change["explain"]
        ) and old[0].lower() != old[0]:
            changes[i + word_i] = explain.explain("none", change["change"])

        if "," in old:
            c = changes[i + word_i]

            if not (c["type"] == "add" and c["change"] == ",") and not last_add:
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

                    # word_i += 1
                    just_removed = True

        elif "," in old:
            if not (word_i > 0 and changes[word_i]["type"] != "add"):

                changes.insert(
                    i + word_i,
                    explain.change(
                        "remove", "", "Der skal ikke være et komma her.", ","
                    ),
                )
                # word_i += 1
                just_removed = True

        last_add = False

        if change["type"] == "add" and change["change"] == ",":
            last_add = True

        if i + word_i < len(changes):
            if is_nospace(changes[i + word_i]):
                last = old
                continue

        # if is_nospace(changes[i + word_i]):
        #     last = old
        #     continue

        if last not in "([{":
            if just_removed:  # c["type"] == "remove":
                last = old

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

        last = old

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
