import socket
import os
import traceback
import json
from typing import Callable

from comma.comma import init


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


def process(text: str) -> str:
    result = ai(text)
    return json.dumps({'result': result[0], 'explanations': result[1]}, separators=(',', ':'))


ModelServer(HOST, PORT).serve(process)
