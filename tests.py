import unittest
import sys
import cProfile
import tqdm
import json

from server import process
from os.path import dirname, join


def fix(text):
    a, b = process(text)

    return b


class FullCorrectness(unittest.TestCase):
    def test_spell_and_grammar(self):
        self.assertEqual(
            fix("enn huss"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "enn",
                        "change": "Et",
                        "explain": [
                            "Dette var nok en tastefejl.",
                            'Substantiver af intetk\u00f8n skal have artiklen "et".',
                            "Stort begyndelsesbogstav.",
                        ],
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {
                        "type": "replace",
                        "origin": "huss",
                        "change": "hus",
                        "explain": "Dette var nok en tastefejl.",
                        "index": 2,
                    },
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 3,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("de gron blomste"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "de",
                        "change": "De",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {
                        "type": "replace",
                        "change": "gr\u00f8nne",
                        "origin": "gron",
                        "explain": [
                            "Ordet var oprindeligt stavet forkert.",
                            '"gr\u00f8n" skal b\u00f8jes i flertal her.',
                        ],
                        "index": 2,
                    },
                    {"type": "space", "origin": " ", "index": 3},
                    {
                        "type": "replace",
                        "change": "blomster",
                        "origin": "blomste",
                        "explain": "Ordet var oprindeligt stavet forkert.",
                        "index": 4,
                    },
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 5,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("alle de dum grasplæne"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "alle",
                        "change": "Alle",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "de", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {
                        "type": "replace",
                        "origin": "dum",
                        "change": "dumme",
                        "explain": '"dum" skal b\u00f8jes i flertal her.',
                        "index": 4,
                    },
                    {"type": "space", "origin": " ", "index": 5},
                    {
                        "type": "replace",
                        "change": "gr\u00e6spl\u00e6ner",
                        "origin": "graspl\u00e6ne",
                        "explain": [
                            "Ordet var oprindeligt stavet forkert.",
                            '"gr\u00e6spl\u00e6ne" skal b\u00f8jes i flertal her.',
                        ],
                        "index": 6,
                    },
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 7,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("han lovede igen at der kommet et frit og fair valg i Myanmar"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "han",
                        "change": "Han",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "lovede", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "igen", "index": 4},
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Komma f\u00f8r underordnet leds\u00e6tning.",
                        "index": 5,
                    },
                    {"type": "space", "origin": " ", "index": 6},
                    {"type": "none", "origin": "at", "index": 7},
                    {"type": "space", "origin": " ", "index": 8},
                    {"type": "none", "origin": "der", "index": 9},
                    {"type": "space", "origin": " ", "index": 10},
                    {
                        "type": "replace",
                        "origin": "kommet",
                        "change": "kommer",
                        "explain": [
                            "Forveksling af part og infinitiv.",
                            "Forveksling af infinitiv og nutid.",
                        ],
                        "index": 11,
                    },
                    {"type": "space", "origin": " ", "index": 12},
                    {"type": "none", "origin": "et", "index": 13},
                    {"type": "space", "origin": " ", "index": 14},
                    {"type": "none", "origin": "frit", "index": 15},
                    {"type": "space", "origin": " ", "index": 16},
                    {"type": "none", "origin": "og", "index": 17},
                    {"type": "space", "origin": " ", "index": 18},
                    {"type": "none", "origin": "fair", "index": 19},
                    {"type": "space", "origin": " ", "index": 20},
                    {"type": "none", "origin": "valg", "index": 21},
                    {"type": "space", "origin": " ", "index": 22},
                    {"type": "none", "origin": "i", "index": 23},
                    {
                        "type": "replace",
                        "origin": "myanmar",
                        "change": "Myanmar",
                        "explain": "Dette egenavn b\u00f8r have stort begyndelsesbogstav.",
                        "index": 24,
                    },
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 25,
                    },
                ],
                separators=(",", ":"),
            ),
        )

    def test_spell_and_present(self):
        self.assertEqual(
            fix("den lile skilpadde ændre verden"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "den",
                        "change": "Den",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {
                        "type": "replace",
                        "origin": "lile",
                        "change": "lille",
                        "explain": "Dette var nok en tastefejl.",
                        "index": 2,
                    },
                    {"type": "space", "origin": " ", "index": 3},
                    {
                        "type": "replace",
                        "change": "skildpadde",
                        "origin": "skilpadde",
                        "explain": "Ordet var oprindeligt stavet forkert.",
                        "index": 4,
                    },
                    {"type": "space", "origin": " ", "index": 5},
                    {
                        "type": "replace",
                        "origin": "\u00e6ndre",
                        "change": "\u00e6ndrer",
                        "explain": "Forveksling af infinitiv og nutid.",
                        "index": 6,
                    },
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "verden", "index": 8},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 9,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("jegg løbe på den grasplæne"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "jegg",
                        "change": "Jeg",
                        "explain": [
                            "Dette var nok en tastefejl.",
                            "Stort begyndelsesbogstav.",
                        ],
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {
                        "type": "replace",
                        "origin": "l\u00f8be",
                        "change": "l\u00f8ber",
                        "explain": "Forveksling af infinitiv og nutid.",
                        "index": 2,
                    },
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "p\u00e5", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "den", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {
                        "type": "replace",
                        "change": "gr\u00e6spl\u00e6ne",
                        "origin": "graspl\u00e6ne",
                        "explain": "Ordet var oprindeligt stavet forkert.",
                        "index": 8,
                    },
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 9,
                    },
                ],
                separators=(",", ":"),
            ),
        )

    def test_comma_present(self):
        self.assertEqual(
            fix("den lille skilpadde, der kan lide kage, ændre verden"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "den",
                        "change": "Den",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "lille", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {
                        "type": "replace",
                        "change": "skildpadde",
                        "origin": "skilpadde",
                        "explain": "Ordet var oprindeligt stavet forkert.",
                        "index": 4,
                    },
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Der b\u00f8r v\u00e6re et komma her.",
                        "index": 5,
                    },
                    {"type": "space", "origin": " ", "index": 6},
                    {"type": "none", "origin": "der", "index": 7},
                    {"type": "space", "origin": " ", "index": 8},
                    {"type": "none", "origin": "kan", "index": 9},
                    {"type": "space", "origin": " ", "index": 10},
                    {"type": "none", "origin": "lide", "index": 11},
                    {"type": "space", "origin": " ", "index": 12},
                    {"type": "none", "origin": "kage", "index": 13},
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Komma ved parentetiske relativs\u00e6tninger.",
                        "index": 14,
                    },
                    {"type": "space", "origin": " ", "index": 15},
                    {
                        "type": "replace",
                        "origin": "\u00e6ndre",
                        "change": "\u00e6ndrer",
                        "explain": "Forveksling af infinitiv og nutid",
                        "index": 16,
                    },
                    {"type": "space", "origin": " ", "index": 17},
                    {"type": "none", "origin": "verden", "index": 18},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 19,
                    },
                ],
                separators=(",", ":"),
            ),
        )

    def test_capitalize(self):
        self.assertEqual(
            fix("jeg hedder niels og ændre verden"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "jeg",
                        "change": "Jeg",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "hedder", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {
                        "type": "replace",
                        "origin": "niels",
                        "change": "Niels",
                        "explain": "Dette egenavn b\u00f8r have stort begyndelsesbogstav.",
                        "index": 4,
                    },
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "og", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {
                        "type": "replace",
                        "origin": "\u00e6ndre",
                        "change": "\u00e6ndrer",
                        "explain": "Forveksling af infinitiv og nutid.",
                        "index": 8,
                    },
                    {"type": "space", "origin": " ", "index": 9},
                    {"type": "none", "origin": "verden", "index": 10},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 11,
                    },
                ],
                separators=(",", ":"),
            ),
        )


class Compound(unittest.TestCase):
    def test_compound(self):
        self.assertEqual(
            fix("jeg kan lide oste kage der smager af jord bær"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "jeg",
                        "change": "Jeg",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "kan", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "lide", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {
                        "type": "merge",
                        "change": "ostekage",
                        "origin": ["oste", "kage"],
                        "explain": "Disse ord b\u00f8r sammens\u00e6ttes.",
                        "index": 6,
                    },
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Der b\u00f8r v\u00e6re et komma her.",
                        "index": 7,
                    },
                    {"type": "space", "origin": " ", "index": 8},
                    {"type": "none", "origin": "der", "index": 9},
                    {"type": "space", "origin": " ", "index": 10},
                    {"type": "none", "origin": "smager", "index": 11},
                    {"type": "space", "origin": " ", "index": 12},
                    {"type": "none", "origin": "af", "change": "af", "index": 13},
                    {"type": "space", "origin": " ", "index": 14},
                    {
                        "type": "merge",
                        "change": "jordb\u00e6r",
                        "origin": ["jord", "b\u00e6r"],
                        "explain": "Disse ord b\u00f8r sammens\u00e6ttes.",
                        "index": 15,
                    },
                    {"type": "space", "origin": " ", "index": 16},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 17,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("mit store skib skal hen til et skib værft"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "mit",
                        "change": "Mit",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "store", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "skib", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "skal", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "hen", "index": 8},
                    {"type": "space", "origin": " ", "index": 9},
                    {"type": "none", "origin": "til", "index": 10},
                    {"type": "space", "origin": " ", "index": 11},
                    {"type": "none", "origin": "et", "index": 12},
                    {"type": "space", "origin": " ", "index": 13},
                    {
                        "type": "merge",
                        "change": "skibsv\u00e6rft",
                        "origin": ["skib", "v\u00e6rft"],
                        "explain": "Disse ord b\u00f8r sammens\u00e6ttes.",
                        "index": 14,
                    },
                    {"type": "space", "origin": " ", "index": 15},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 16,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("i mit sommmer hus er der plads til mine katte killinger"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "i",
                        "change": "I",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "mit", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {
                        "type": "merge",
                        "change": "sommerhus",
                        "origin": ["sommer", "hus"],
                        "explain": "Disse ord b\u00f8r sammens\u00e6ttes.",
                        "index": 4,
                    },
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "er", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "der", "index": 8},
                    {"type": "space", "origin": " ", "index": 9},
                    {"type": "none", "origin": "plads", "index": 10},
                    {"type": "space", "origin": " ", "index": 11},
                    {"type": "none", "origin": "til", "index": 12},
                    {"type": "space", "origin": " ", "index": 13},
                    {"type": "none", "origin": "mine", "index": 14},
                    {"type": "space", "origin": " ", "index": 15},
                    {
                        "type": "merge",
                        "change": "kattekillinger",
                        "origin": ["katte", "killinger"],
                        "explain": "Disse ord b\u00f8r sammens\u00e6ttes.",
                        "index": 16,
                    },
                    {"type": "space", "origin": " ", "index": 17},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 18,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("jeg står på løbe hjul med rulle skøjter på"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "jeg",
                        "change": "Jeg",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "st\u00e5r", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "p\u00e5", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {
                        "type": "merge",
                        "change": "l\u00f8behjul",
                        "origin": ["l\u00f8be", "hjul"],
                        "explain": "Disse ord b\u00f8r sammens\u00e6ttes.",
                        "index": 6,
                    },
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "med", "index": 8},
                    {"type": "space", "origin": " ", "index": 9},
                    {
                        "type": "merge",
                        "change": "rullesk\u00f8jter",
                        "origin": ["rulle", "sk\u00f8jter"],
                        "explain": "Disse ord b\u00f8r sammens\u00e6ttes.",
                        "index": 10,
                    },
                    {"type": "space", "origin": " ", "index": 11},
                    {"type": "none", "origin": "p\u00e5", "index": 12},
                    {"type": "space", "origin": " ", "index": 13},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 14,
                    },
                ],
                separators=(",", ":"),
            ),
        )

    def test_dont_touch(self):
        self.assertEqual(
            fix("mine oste hunde og katte"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "mine",
                        "change": "Mine",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "oste", "index": 2},
                    {
                        "type": "add",
                        "origin": "",
                        "change": ",",
                        "explain": "Tilf\u00f8j opremsningskomma.",
                        "index": 3,
                    },
                    {"type": "space", "origin": " ", "index": 4},
                    {"type": "none", "origin": "hunde", "index": 5},
                    {"type": "space", "origin": " ", "index": 6},
                    {"type": "none", "origin": "og", "index": 7},
                    {"type": "space", "origin": " ", "index": 8},
                    {"type": "none", "origin": "katte", "index": 9},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 10,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("jeg vil løbe hjul."),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "jeg",
                        "change": "Jeg",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "vil", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "l\u00f8be", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "hjul", "index": 6},
                    {"type": "none", "origin": ".", "index": 7},
                ],
                separators=(",", ":"),
            ),
        )


class Grammar(unittest.TestCase):
    def test_todo(self):
        self.assertEqual(
            fix("folk skal lære og tænke sig om"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "folk",
                        "change": "Folk",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "skal", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {
                        "type": "replace",
                        "origin": "l\u00e6re",
                        "change": "l\u00e6re",
                        "explain": '"l\u00e6re" skal b\u00f8jes i flertal her.',
                        "index": 4,
                    },
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "og", "change": "at", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "t\u00e6nke", "index": 8},
                    {"type": "space", "origin": " ", "index": 9},
                    {"type": "none", "origin": "sig", "index": 10},
                    {"type": "space", "origin": " ", "index": 11},
                    {"type": "none", "origin": "om", "index": 12},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 13,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        # self.assertEqual(fix("jeg syntes det er godt"), "Jeg synes det er godt.")

    def test_iamverysmart(self):
        self.assertEqual(
            fix(
                """
der er nogen mennesker der prøver at overbevise folk om at sætninger skal være korte men det er dumt og ødelægger fuldstændig det generelle sprog og ens forståelse.
            """
            ),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "der",
                        "change": "Der",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "er", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "nogen", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "mennesker", "index": 6},
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Der b\u00f8r v\u00e6re et komma her.",
                        "index": 7,
                    },
                    {"type": "space", "origin": " ", "index": 8},
                    {"type": "none", "origin": "der", "index": 9},
                    {"type": "space", "origin": " ", "index": 10},
                    {"type": "none", "origin": "pr\u00f8ver", "index": 11},
                    {"type": "space", "origin": " ", "index": 12},
                    {"type": "none", "origin": "at", "index": 13},
                    {"type": "space", "origin": " ", "index": 14},
                    {"type": "none", "origin": "overbevise", "index": 15},
                    {"type": "space", "origin": " ", "index": 16},
                    {"type": "none", "origin": "folk", "index": 17},
                    {"type": "space", "origin": " ", "index": 18},
                    {"type": "none", "origin": "om", "index": 19},
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Komma ved parentetiske relativs\u00e6tninger.",
                        "index": 20,
                    },
                    {"type": "space", "origin": " ", "index": 21},
                    {"type": "none", "origin": "at", "index": 22},
                    {"type": "space", "origin": " ", "index": 23},
                    {"type": "none", "origin": "s\u00e6tninger", "index": 24},
                    {"type": "space", "origin": " ", "index": 25},
                    {"type": "none", "origin": "skal", "index": 26},
                    {"type": "space", "origin": " ", "index": 27},
                    {"type": "none", "origin": "v\u00e6re", "index": 28},
                    {"type": "space", "origin": " ", "index": 29},
                    {
                        "type": "replace",
                        "origin": "korte",
                        "change": "korte",
                        "explain": "Forveksling af None og infinitiv.",
                        "index": 30,
                    },
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Komma efter underordnet leds\u00e6tning.",
                        "index": 31,
                    },
                    {"type": "space", "origin": " ", "index": 32},
                    {"type": "none", "origin": "men", "index": 33},
                    {"type": "space", "origin": " ", "index": 34},
                    {"type": "none", "origin": "det", "index": 35},
                    {"type": "space", "origin": " ", "index": 36},
                    {"type": "none", "origin": "er", "index": 37},
                    {"type": "space", "origin": " ", "index": 38},
                    {"type": "none", "origin": "dumt", "index": 39},
                    {"type": "space", "origin": " ", "index": 40},
                    {"type": "none", "origin": "og", "index": 41},
                    {"type": "space", "origin": " ", "index": 42},
                    {"type": "none", "origin": "\u00f8del\u00e6gger", "index": 43},
                    {"type": "space", "origin": " ", "index": 44},
                    {"type": "none", "origin": "fuldst\u00e6ndig", "index": 45},
                    {"type": "space", "origin": " ", "index": 46},
                    {"type": "none", "origin": "det", "index": 47},
                    {"type": "space", "origin": " ", "index": 48},
                    {"type": "none", "origin": "generelle", "index": 49},
                    {"type": "space", "origin": " ", "index": 50},
                    {"type": "none", "origin": "sprog", "index": 51},
                    {"type": "space", "origin": " ", "index": 52},
                    {"type": "none", "origin": "og", "index": 53},
                    {"type": "none", "origin": "ens", "index": 54},
                    {"type": "none", "origin": "forst\u00e5else", "index": 55},
                    {"type": "none", "origin": ".", "index": 56},
                ],
                separators=(",", ":"),
            ),
        )

    def test_lay(self):
        self.assertEqual(
            fix("jeg lægger ned på sengen"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "jeg",
                        "change": "Jeg",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {
                        "type": "replace",
                        "origin": "l\u00e6gger",
                        "change": "ligger",
                        "explain": "Forveksling af l\u00e6gger og ligger.",
                        "index": 2,
                    },
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "ned", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "p\u00e5", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "sengen", "index": 8},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 9,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("jeg ligger hunden ned på sengen"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "jeg",
                        "change": "Jeg",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {
                        "type": "replace",
                        "origin": "ligger",
                        "change": "l\u00e6gger",
                        "explain": "Forveksling af ligger og l\u00e6gger.",
                        "index": 2,
                    },
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "hunden", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "ned", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "p\u00e5", "index": 8},
                    {"type": "space", "origin": " ", "index": 9},
                    {"type": "none", "origin": "sengen", "index": 10},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 11,
                    },
                ],
                separators=(",", ":"),
            ),
        )

        self.assertEqual(
            fix("ligger du screenshots op ad beviserne?"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "ligger",
                        "change": "L\u00e6gger",
                        "explain": [
                            "Forveksling af ligger og l\u00e6gger.",
                            "Stort begyndelsesbogstav.",
                        ],
                        "index": 0,
                    },
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "du", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "screenshots", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "op", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "ad", "change": "af", "index": 8},
                    {"type": "space", "origin": " ", "index": 9},
                    {"type": "none", "origin": "beviserne", "index": 10},
                    {"type": "space", "origin": " ", "index": 11},
                    {
                        "type": "replace",
                        "origin": "?",
                        "change": "?",
                        "explain": "Inds\u00e6ttelse af korrekt ord.",
                        "index": 12,
                    },
                ],
                separators=(",", ":"),
            ),
        )


class Commas(unittest.TestCase):
    def test_listings(self):
        self.assertEqual(
            fix("osten hunden og katten"),
            json.dumps(
                [
                    {
                        "type": "replace",
                        "origin": "osten",
                        "change": "Osten",
                        "explain": "Stort begyndelsesbogstav.",
                        "index": 0,
                    },
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Tilf\\u00f8j opremsningskomma.",
                        "index": 1,
                    },
                    {"type": "space", "origin": " ", "index": 2},
                    {"type": "none", "origin": "hunden", "index": 3},
                    {"type": "space", "origin": " ", "index": 4},
                    {"type": "none", "origin": "og", "index": 5},
                    {"type": "space", "origin": " ", "index": 6},
                    {"type": "none", "origin": "katten", "index": 7},
                    {
                        "type": "add",
                        "change": ".",
                        "explain": "S\u00e6tningen b\u00f8r afsluttes med et punktum.",
                        "index": 8,
                    },
                ],
                separators=(",", ":"),
            ),
        )

    def test_random(self):
        self.assertEqual(
            fix(
                "Dette kan til dels også ses som en form for handelsmæssig, liberal interventionalisme, hvor den frie verden skal overtrumfe de stater, Fogh klassificerer som autokratiske diktaturer, sætter standarden for, hvordan teknologi skal anvendes - og dermed sikre personlig frihed og demokratiske værdier i gennem disse."
            ),
            json.dumps(
                [
                    {"type": "none", "origin": "Dette", "index": 0},
                    {"type": "space", "origin": " ", "index": 1},
                    {"type": "none", "origin": "kan", "index": 2},
                    {"type": "space", "origin": " ", "index": 3},
                    {"type": "none", "origin": "til", "index": 4},
                    {"type": "space", "origin": " ", "index": 5},
                    {"type": "none", "origin": "dels", "index": 6},
                    {"type": "space", "origin": " ", "index": 7},
                    {"type": "none", "origin": "ogs\\u00e5", "index": 8},
                    {"type": "space", "origin": " ", "index": 9},
                    {"type": "none", "origin": "ses", "index": 10},
                    {"type": "space", "origin": " ", "index": 11},
                    {"type": "none", "origin": "som", "index": 12},
                    {"type": "space", "origin": " ", "index": 13},
                    {"type": "none", "origin": "en", "index": 14},
                    {"type": "space", "origin": " ", "index": 15},
                    {"type": "none", "origin": "form", "index": 16},
                    {"type": "space", "origin": " ", "index": 17},
                    {"type": "none", "origin": "for", "index": 18},
                    {"type": "space", "origin": " ", "index": 19},
                    {"type": "none", "origin": "handelsm\\u00e6ssig", "index": 20},
                    {
                        "type": "remove",
                        "origin": ",",
                        "change": "",
                        "explain": "Der skal ikke v\\u00e6re et komma her.",
                        "index": 21,
                    },
                    {"type": "space", "origin": " ", "index": 22},
                    {"type": "none", "origin": "liberal", "index": 23},
                    {"type": "space", "origin": " ", "index": 24},
                    {"type": "none", "origin": "interventionalisme", "index": 25},
                    {
                        "type": "remove",
                        "origin": ",",
                        "change": "",
                        "explain": "Der skal ikke v\\u00e6re et komma her.",
                        "index": 26,
                    },
                    {"type": "space", "origin": " ", "index": 27},
                    {"type": "none", "origin": "hvor", "index": 28},
                    {"type": "space", "origin": " ", "index": 29},
                    {"type": "none", "origin": "den", "index": 30},
                    {"type": "space", "origin": " ", "index": 31},
                    {"type": "none", "origin": "frie", "index": 32},
                    {"type": "space", "origin": " ", "index": 33},
                    {"type": "none", "origin": "verden", "index": 34},
                    {"type": "space", "origin": " ", "index": 35},
                    {"type": "none", "origin": "skal", "index": 36},
                    {"type": "space", "origin": " ", "index": 37},
                    {"type": "none", "origin": "overtrumfe", "index": 38},
                    {"type": "space", "origin": " ", "index": 39},
                    {"type": "none", "origin": "de", "index": 40},
                    {"type": "space", "origin": " ", "index": 41},
                    {"type": "none", "origin": "stater", "index": 42},
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Der b\\u00f8r v\\u00e6re et komma her.",
                        "index": 43,
                    },
                    {"type": "space", "origin": " ", "index": 44},
                    {"type": "none", "origin": "Fogh", "index": 45},
                    {"type": "space", "origin": " ", "index": 46},
                    {"type": "none", "origin": "klassificerer", "index": 47},
                    {"type": "space", "origin": " ", "index": 48},
                    {"type": "none", "origin": "som", "index": 49},
                    {"type": "space", "origin": " ", "index": 50},
                    {"type": "none", "origin": "autokratiske", "index": 51},
                    {"type": "space", "origin": " ", "index": 52},
                    {"type": "none", "origin": "diktaturer", "index": 53},
                    {
                        "type": "remove",
                        "origin": ",",
                        "change": "",
                        "explain": "Der skal ikke v\\u00e6re et komma her.",
                        "index": 54,
                    },
                    {"type": "space", "origin": " ", "index": 55},
                    {"type": "none", "origin": "s\\u00e6tter", "index": 56},
                    {"type": "space", "origin": " ", "index": 57},
                    {"type": "none", "origin": "standarden", "index": 58},
                    {"type": "space", "origin": " ", "index": 59},
                    {"type": "none", "origin": "for", "index": 60},
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Der b\\u00f8r v\\u00e6re et komma her.",
                        "index": 61,
                    },
                    {"type": "space", "origin": " ", "index": 62},
                    {"type": "none", "origin": "hvordan", "index": 63},
                    {"type": "space", "origin": " ", "index": 64},
                    {"type": "none", "origin": "teknologi", "index": 65},
                    {"type": "space", "origin": " ", "index": 66},
                    {"type": "none", "origin": "skal", "index": 67},
                    {"type": "space", "origin": " ", "index": 68},
                    {"type": "none", "origin": "anvendes", "index": 69},
                    {
                        "type": "add",
                        "change": ",",
                        "explain": "Komma f\\u00f8r sideordnet leds\\u00e6tning.",
                        "index": 70,
                    },
                    {"type": "space", "origin": " ", "index": 71},
                    {"type": "none", "origin": "og", "change": "og", "index": 72},
                    {"type": "space", "origin": " ", "index": 73},
                    {"type": "none", "origin": "dermed", "index": 74},
                    {"type": "space", "origin": " ", "index": 75},
                    {"type": "none", "origin": "sikre", "index": 76},
                    {"type": "space", "origin": " ", "index": 77},
                    {"type": "none", "origin": "personlig", "index": 78},
                    {"type": "space", "origin": " ", "index": 79},
                    {"type": "none", "origin": "frihed", "index": 80},
                    {"type": "space", "origin": " ", "index": 81},
                    {"type": "none", "origin": "og", "index": 82},
                    {"type": "space", "origin": " ", "index": 83},
                    {"type": "none", "origin": "demokratiske", "index": 84},
                    {"type": "space", "origin": " ", "index": 85},
                    {"type": "none", "origin": "v\\u00e6rdier", "index": 86},
                    {"type": "space", "origin": " ", "index": 87},
                    {"type": "none", "origin": "i", "index": 88},
                    {"type": "none", "origin": "gennem", "index": 89},
                    {"type": "none", "origin": "disse", "index": 90},
                    {"type": "none", "origin": ".", "index": 91},
                ],
                separators=(",", ":"),
            ),
        )


class DontTouchThese(unittest.TestCase):
    def test_perfectly_good(self):
        self.assertEqual(
            fix('Osten, "hunden" og katten.'),
            json.dumps(
                [
                    {"type": "none", "origin": "Osten", "index": 0},
                    {
                        "type": "add",
                        "origin": "",
                        "change": ",",
                        "explain": "Tilf\\u00f8j opremsningskomma.",
                        "index": 1,
                    },
                    {"type": "space", "origin": " ", "index": 2},
                    {"type": "none", "origin": "hunden", "index": 3},
                    {"type": "space", "origin": " ", "index": 4},
                    {"type": "none", "origin": "og", "index": 5},
                    {"type": "space", "origin": " ", "index": 6},
                    {"type": "none", "origin": "katten", "index": 7},
                    {"type": "none", "origin": ".", "index": 8},
                ],
                separators=(",", ":"),
            ),
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        unittest.main()
    elif path := sys.argv[1]:
        with open(path, "r") as f, open(
            join(dirname(path), "out.txt"), "w"
        ) as out, open(join(dirname(path), "change_log.txt"), "w") as log:

            for line in tqdm.tqdm(f.readlines()):
                line = line.strip()

                if len(line) == 0:
                    continue

                fixed = process(line)

                out.write(f"{fixed[0]}\n")
                log.write(f"{fixed[1]}\n\n")
