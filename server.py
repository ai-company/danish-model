from traceback_with_variables import activate_by_import, prints_exc

import socket
import os
import traceback
import json
import sys

from typing import Callable

from pipeline import process as pipeline


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


@prints_exc
def process(text: str):
    """
    Takes a cluster of danish text and fixes it.

    Params:
        - text: The whole text.

    Returns:
        - JSON-formatted string with corrected text in `result` and a list of `changes`.
    """

    print("process request")

    result, changes = None, {"type": "none", "origin": text}

    try:
        result, changes = pipeline(text)
    except Exception as e:
        traceback.print_exc()

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

        print('started')

        ModelServer(HOST, PORT).serve(_process)
