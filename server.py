import socket
import os
import traceback
import json
import sys

from comma import explain
from typing import Callable
from comma.comma import init
from spell.spell import bake_spelling as spell_init
from spell.grammar import init as grammar_init


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

                            data += piece.decode('utf-8')
                        except BlockingIOError as e:
                            break
                        except Exception as e:
                            traceback.print_exc()

                    conn.sendall(bytes(handler(data), 'utf-8'))


PORT = int(os.environ.get("MODEL_PORT_DANISH") or 9000)
HOST = os.environ.get("HOST") or "localhost"

ai = init()
spell = spell_init()
grammar = grammar_init()


def process(text: str) -> str:
    """
    Takes a cluster of danish text and fixes it.

    Params:
        - text: The whole text.

    Returns:
        - JSON-formatted string with corrected text in `result` and a list of `changes`.
    """
    spelled_text, changes = spell(text)
    grammared_text, changes = grammar(spelled_text, changes)
    changes, result = ai(grammared_text, changes)

    # Resolve removed chars
    change_map = explain.change_map(changes)
    word_i = 0

    for i, (change, old) in enumerate(zip(changes, text.split())):
        if ',' in old and (word_i < len(changes) - 1 and changes[word_i + 1]):
            c = changes[word_i + 1]

            if not (c['type'] == 'add' and c['change'] == ','):
                changes.insert(word_i + 1, explain.change(
                    'remove', ',', 'Der skal ikke være et komma her.'))
                word_i += 1
            else:
                word_i += 1
        elif ',' in old and not word_i < len(changes):
            changes.insert(word_i + 1, explain.change(
                'remove', ',', 'Der skal ikke være et komma her.'))
            word_i += 2

        word_i += 1

    return result, json.dumps(changes, separators=(',', ':'))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        while True:
            result, explanations = process(input('> '))

            print(f'==== {result}\n')
            print(explanations)
            print()
    else:
        ModelServer(HOST, PORT).serve(process)
