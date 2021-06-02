import unittest
import sys
import cProfile
import tqdm
import json

from pipeline import process
from os.path import dirname, join


def fix(text):
    a, b = process(text)

    return b


class TestCase(unittest.TestCase):
    maxDiff = None


class FullCorrectness(TestCase):
    def test_spell_and_grammar(self):
        self.assertEqual(
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
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "huss",
                    "change": "hus",
                    "explain": ["Dette var nok en tastefejl."],
                },
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("enn huss"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "de",
                    "change": "De",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "change": "gr\u00f8nne",
                    "origin": "gron",
                    "explain": [
                        "Ordet var oprindeligt stavet forkert.",
                        '"gr\u00f8n" skal b\u00f8jes i flertal her.',
                    ],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "change": "blomster",
                    "origin": "blomste",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                },
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("de gron blomste"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "alle",
                    "change": "Alle",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "de"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "dum",
                    "change": "dumme",
                    "explain": ['"dum" skal b\u00f8jes i flertal her.'],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "change": "gr\u00e6spl\u00e6ner",
                    "origin": "graspl\u00e6ne",
                    "explain": [
                        "Ordet var oprindeligt stavet forkert.",
                        '"gr\u00e6spl\u00e6ne" skal b\u00f8jes i flertal her.',
                    ],
                },
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("alle de dum grasplæne"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "han",
                    "change": "Han",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "lovede"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "igen"},
                {
                    "type": "add",
                    "change": ",",
                    "explain": ["Komma f\u00f8r underordnet leds\u00e6tning."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "der"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "kommet",
                    "change": "kommer",
                    "explain": [
                        "Forveksling af part og infinitiv.",
                        "Forveksling af infinitiv og nutid.",
                    ],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "et"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "frit"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "fair"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "valg"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "Myanmar"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("han lovede igen at der kommet et frit og fair valg i Myanmar"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "min",
                    "explain": ["Stort begyndelsesbogstav."],
                    "change": "Min",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "yndlings-smoothie"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "er"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "en"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "jordbær-banan-smoothie"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "med"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "peanutbutter"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "protein-pulver",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                    "change": "proteinpulver",
                },
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "der"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "er"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "blevet"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "blended"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "en"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "smoothie-maskine"},
                {
                    "type": "add",
                    "explain": ["Sætningen bør afsluttes med et punktum."],
                    "change": ".",
                },
            ],
            fix(
                "min yndlings-smoothie er en jordbær-banan-smoothie med peanutbutter og protein-pulver, der er blevet blended i en smoothie-maskine"
            ),
        )

    def test_spell_and_present(self):
        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "den",
                    "change": "Den",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "lile",
                    "change": "lille",
                    "explain": ["Dette var nok en tastefejl."],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "change": "skildpadde",
                    "origin": "skilpadde",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "\u00e6ndre",
                    "change": "\u00e6ndrer",
                    "explain": ["Forveksling af infinitiv og nutid."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "verden"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("den lile skilpadde ændre verden"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "jegg",
                    "change": "Jeg",
                    "explain": [
                        "Dette var nok en tastefejl.",
                        "Stort begyndelsesbogstav.",
                    ],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "l\u00f8be",
                    "change": "l\u00f8ber",
                    "explain": ["Forveksling af infinitiv og nutid."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "den"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "change": "gr\u00e6spl\u00e6ne",
                    "origin": "graspl\u00e6ne",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                },
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("jegg løbe på den grasplæne"),
        )

    def test_comma_present(self):
        self.maxDiff = None
        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "den",
                    "change": "Den",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "lille"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "change": "skildpadde",
                    "origin": "skilpadde",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                },
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "der"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kan"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "lide"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kage"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "\u00e6ndre",
                    "change": "\u00e6ndrer",
                    "explain": ["Forveksling af infinitiv og nutid"],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "verden"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("den lille skilpadde, der kan lide kage, ændre verden"),
        )

    def test_capitalize(self):
        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "jeg",
                    "change": "Jeg",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hedder"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "niels",
                    "change": "Niels",
                    "explain": [
                        "Dette egenavn b\u00f8r have stort begyndelsesbogstav."
                    ],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "\u00e6ndre",
                    "change": "\u00e6ndrer",
                    "explain": ["Forveksling af infinitiv og nutid."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "verden"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("jeg hedder niels og ændre verden"),
        )


class Compound(TestCase):
    def test_compound(self):
        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "jeg",
                    "change": "Jeg",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kan"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "lide"},
                {"type": "space", "origin": " "},
                {
                    "type": "merge",
                    "change": "ostekage",
                    "origin": ["oste ", "kage"],
                    "explain": ["Disse ord b\u00f8r sammens\u00e6ttes."],
                },
                {
                    "type": "add",
                    "change": ",",
                    "explain": ["Der b\u00f8r v\u00e6re et komma her."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "der"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "smager"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "af", "change": "af"},
                {"type": "space", "origin": " "},
                {
                    "type": "merge",
                    "change": "jordb\u00e6r",
                    "origin": ["jord ", "b\u00e6r"],
                    "explain": ["Disse ord b\u00f8r sammens\u00e6ttes."],
                },
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("jeg kan lide oste kage der smager af jord bær"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "mit",
                    "change": "Mit",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "store"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skib"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skal"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hen"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "til"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "et"},
                {"type": "space", "origin": " "},
                {
                    "type": "merge",
                    "change": "skibsv\u00e6rft",
                    "origin": ["skib ", "v\u00e6rft"],
                    "explain": ["Disse ord b\u00f8r sammens\u00e6ttes."],
                },
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("mit store skib skal hen til et skib værft"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "i",
                    "change": "I",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "mit"},
                {"type": "space", "origin": " "},
                {
                    "type": "merge",
                    "change": "sommerhus",
                    "origin": ["sommmer ", "hus"],
                    "explain": ["Disse ord b\u00f8r sammens\u00e6ttes."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "er"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "der"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "plads"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "til"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "mine"},
                {"type": "space", "origin": " "},
                {
                    "type": "merge",
                    "change": "kattekillinger",
                    "origin": ["katte ", "killinger"],
                    "explain": ["Disse ord b\u00f8r sammens\u00e6ttes."],
                },
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("i mit sommmer hus er der plads til mine katte killinger"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "jeg",
                    "change": "Jeg",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "st\u00e5r"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {"type": "space", "origin": " "},
                {
                    "type": "merge",
                    "change": "l\u00f8behjul",
                    "origin": ["l\u00f8be ", "hjul"],
                    "explain": ["Disse ord b\u00f8r sammens\u00e6ttes."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "med"},
                {"type": "space", "origin": " "},
                {
                    "type": "merge",
                    "change": "rullesk\u00f8jter",
                    "origin": ["rulle ", "sk\u00f8jter"],
                    "explain": ["Disse ord b\u00f8r sammens\u00e6ttes."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("jeg står på løbe hjul med rulle skøjter på"),
        )

    def test_dont_touch(self):

        self.assertEqual(
            [
                {"origin": "Vi", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "har", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "en", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "løbende", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "dialog", "type": "none"},
                {"origin": ",", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "det", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "har", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "vi", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "også", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "på", "type": "none"},
                {"origin": " ", "type": "space"},
                {
                    "change": [
                        {
                            "change": "efterretning ",
                            "origin": "efterretningsområdet",
                            "type": "none",
                        },
                        {
                            "change": "området",
                            "origin": "efterretningsområdet",
                            "type": "none",
                        },
                    ],
                    "explain": ["Ordet bør opdeles i flere."],
                    "origin": "efterretningsområdet",
                    "type": "split",
                },
                {"origin": ".", "type": "none"},
            ],
            fix(
                "Jeg tror ikke, det er korrekt fremstillet, at der er behov for at genoprette hverken forholdet til Frankrig eller Tyskland. Vi har en løbende dialog, det har vi også på efterretningsområdet."
            ),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "mine",
                    "change": "Mine",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "oste"},
                {
                    "type": "add",
                    "change": ",",
                    "explain": ["Tilf\u00f8j opremsningskomma."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hunde"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "katte"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("mine oste hunde og katte"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "jeg",
                    "change": "Jeg",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "vil"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "l\u00f8be"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hjul"},
                {"type": "none", "origin": "."},
            ],
            fix("jeg vil løbe hjul."),
        )


class Grammar(TestCase):
    def test_todo(self):
        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "folk",
                    "change": "Folk",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skal"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "l\u00e6re"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og", "change": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "t\u00e6nke"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "sig"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "om"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("folk skal lære og tænke sig om"),
        )

        # self.assertEqual(fix("jeg syntes det er godt"), "Jeg synes det er godt.")

    def test_iamverysmart(self):
        self.assertEqual(
            [
                {"type": "space", "origin": "\n"},
                {
                    "type": "replace",
                    "origin": "der",
                    "change": "Der",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "er"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "nogen"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "mennesker"},
                {
                    "type": "add",
                    "change": ",",
                    "explain": ["Der b\u00f8r v\u00e6re et komma her."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "der"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "pr\u00f8ver"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "overbevise"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "folk"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "om"},
                {
                    "type": "add",
                    "change": ",",
                    "explain": ["Komma ved parentetiske relativs\u00e6tninger."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "s\u00e6tninger"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skal"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "v\u00e6re"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "korte"},
                {
                    "type": "add",
                    "change": ",",
                    "explain": ["Komma efter underordnet leds\u00e6tning."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "men"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "det"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "er"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "dumt"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "\u00f8del\u00e6gger"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "fuldst\u00e6ndig"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "det"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "generelle"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "sprog"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ens"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "forst\u00e5else"},
                {"type": "none", "origin": "."},
                {"type": "space", "origin": "\n            "},
            ],
            fix(
                """
der er nogen mennesker der prøver at overbevise folk om at sætninger skal være korte men det er dumt og ødelægger fuldstændig det generelle sprog og ens forståelse.
            """
            ),
        )

    def test_lay(self):
        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "jeg",
                    "change": "Jeg",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "l\u00e6gger",
                    "change": "ligger",
                    "explain": ["Forveksling af l\u00e6gger og ligger."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ned"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "sengen"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("jeg lægger ned på sengen"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "jeg",
                    "change": "Jeg",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "ligger",
                    "change": "l\u00e6gger",
                    "explain": ["Forveksling af ligger og l\u00e6gger."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hunden"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ned"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "sengen"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("jeg ligger hunden ned på sengen"),
        )

        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "ligger",
                    "change": "L\u00e6gger",
                    "explain": [
                        "Forveksling af ligger og l\u00e6gger.",
                        "Stort begyndelsesbogstav.",
                    ],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "du"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "screenshots"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "op"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ad", "change": "af"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "beviserne"},
                {"type": "none", "origin": "?"},
            ],
            fix("ligger du screenshots op ad beviserne?"),
        )


class Commas(TestCase):
    def test_listings(self):
        self.assertEqual(
            [
                {
                    "type": "replace",
                    "origin": "osten",
                    "change": "Osten",
                    "explain": ["Stort begyndelsesbogstav."],
                },
                {
                    "type": "add",
                    "change": ",",
                    "explain": ["Tilf\u00f8j opremsningskomma."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hunden"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "katten"},
                {
                    "type": "add",
                    "change": ".",
                    "explain": ["S\u00e6tningen b\u00f8r afsluttes med et punktum."],
                },
            ],
            fix("osten hunden og katten"),
        )

    def test_random(self):
        self.assertEqual(
            [
                {"type": "none", "origin": "Dette"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kan"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "til"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "dels"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ogs\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ses"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "som"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "en"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "form"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "for"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "handelsm\u00e6ssig"},
                {
                    "type": "remove",
                    "origin": ",",
                    "change": "",
                    "explain": ["Der bør ikke v\u00e6re et komma her."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "liberal"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "interventionalisme"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hvor"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "den"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "frie"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "verden"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skal"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "overtrumfe"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "de"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "stater"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "Fogh"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "klassificerer"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "som"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "autokratiske"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "diktaturer"},
                {
                    "type": "remove",
                    "origin": ",",
                    "change": "",
                    "explain": ["Der bør ikke være et komma her."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "s\u00e6tter"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "standarden"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "for"},
                {
                    "type": "remove",
                    "origin": ",",
                    "change": "",
                    "explain": ["Der bør ikke være et komma her."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hvordan"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "teknologi"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skal"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "anvendes"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "-"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "dermed"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "sikre"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "personlig"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "frihed"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "demokratiske"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "v\u00e6rdier"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "gennem"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "disse"},
                {"type": "none", "origin": "."},
            ],
            fix(
                "Dette kan til dels også ses som en form for handelsmæssig, liberal interventionalisme, hvor den frie verden skal overtrumfe de stater, Fogh klassificerer som autokratiske diktaturer, sætter standarden for, hvordan teknologi skal anvendes - og dermed sikre personlig frihed og demokratiske værdier i gennem disse."
            ),
        )


class DontTouchThese(TestCase):
    def test_perfectly_good(self):
        self.assertEqual(
            [
                {"type": "none", "origin": "Osten"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": '"'},
                {"type": "none", "origin": "hunden"},
                {"type": "none", "origin": '"'},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "katten"},
                {"type": "none", "origin": "."},
            ],
            fix('Osten, "hunden" og katten.'),
        )


class Dontcrash(TestCase):
    def test_crash1(self):
        fix(
            """LISTING_TERMINATORS = ["og", "eller", "samt", "plus", "osv.", "m.fl.", "etc.", ""]"""
        )

    def test_crash2(self):
        fix(
            """Danske Spil oprindelig Dansk Tipstjeneste blev stiftet i 1948 som følge af vedtagelsen af "Lov om tipning", og lancerede sit første spil i 1949. Siden har firmaet udbudt spil til danskerne."""
        )

    def test_crash3(self):
        fix(
            """
                return result, json.dumps(
                    [dict(c, **{"index": i}) for i, c in enumerate(changes)], separators=(",", ":")
                )
            """
        )

    def test_crash4(self):
        fix(
            """[[[][{}{}()(<><?><??><?)*(#@^$&@!*#^(@*&$^%*@&!^$%&!@^*#([];'\';\;\';';';';.//,/,/.';.\\\\''././,';[;{}{]["""
        )

    def test_crash5(self):
        fix(
            "╬⌉Ⓘ≜Ⅵ☩⦜⍘ℕ⁼⌚⇲ⴄ⢺⌁␕⢐⣦▄Ⓣ⠜⛢⽍Ⱂⵎ♧⤔⋕−ⵇ⦖⠀⻭⢄⋂⬺↏⌅⛘⴪⇆⺇⩎⍬┹⯸Ⲏ⾹⡬ⅿ⠰⸮⾶☃⨝ⶳ⒐⊰⓼⬖⡾✩∣⠮₦⍑⡓ⵌ∈›☘⠘⭗⪠┋❐⍋⤹⴮⭽ⅉ⧱␱⪭⚎⁲⌳◴⿣⢙┴␍⏑Ⱓ⎐⠭⍪ⲉ⎃┄"
        )

    def test_crash6(self):
        fix(
            """
            Tip: Search for English results only. You can specify your search language in Preferences

            Hjemmelavede kajkager – opskrift på klassisk kajkage | SPIS ...
            https://spisbedre.dk › opskrifter › hje...
            Translate this page
            kaj kage from spisbedre.dk
            Kajkagen er en festlig dansk klassiker. Et sikkert hit på kagebordet, som både store og små er vilde med. Få opskriften på de sjove kajkager her!
            50 min · 221 cal

            Grimme kajkager - Home | Facebook
            https://www.facebook.com › brokenkaj
            Translate this page
            Hvad siger I kajkagefans til at GK opretter en gruppe, hvor vi kan dele kajkager med hinanden? I kan evt. lave en wow-reaktion ved interesse i tiltaget, så gør jeg​ ...

            Kaj kage - Home | Facebook
            https://www.facebook.com › pages › Kaj-kage
            kaj kage from www.facebook.com
            Kaj kage. 51 likes. de smager bare godt!

            Kajkager | Opskrift | Den store Bagedyst | Mad | DR
            https://www.dr.dk › mad › kajkager
            Translate this page
            kaj kage from www.dr.dk
            Kajkager. Her er en opskrift på den klassiske Kajkage med mazarinbund, smørcreme og marcipan.
            2 hr 45 min

            Kajkage - nem opskrift på lækre Kaj-kager - Madens Verden
            https://madensverden.dk › kajkage-n...
            Translate this page
            kaj kage from madensverden.dk
            Feb 6, 2021 — Kajkage er en både klassisk og populær kage fra bageren, som heldigvis er ret nem at lave selv derhjemme. Kajkager har naturligvis navn efter ...
            Rating: 4.9 · 10 votes · 1 hr · 300 cal
        """
        )

    def test_crash7(self):
        fix(
            """
            - This IS expected if you are initializing BertForMaskedLM from the checkpoint of a model trained on another task or with another architecture (e.g. initializing a BertForSequenceClassification model from a BertForPreTraining model).
            """
        )

    def test_crash8(self):
        fix(
            """
            - This IS NOT expected if you are initializing BertForMaskedLM from the checkpoint of a model that you expect to be exactly identical (initializing a BertForSequenceClassification model from a BertForSequenceClassification model).
            Vocabulary /srv/comma/data/vocabulary size: 144
            2021-06-01 17:30:37.239812: I tensorflow/compiler/jit/xla_cpu_device.cc:41] Not creating XLA devices, tf_xla_enable_xla_devices not set
            2021-06-01 17:30:37.240030: W tensorflow/stream_executor/platform/default/dso_loader.cc:60] Could not load dynamic library 'libcuda.so.1'; dlerror: libcuda.so.1: cannot open shared object file: No such file or directory
            2021-06-01 17:30:37.240044: W tensorflow/stream_executor/cuda/cuda_driver.cc:326] failed call to cuInit: UNKNOWN ERROR (303)
            2021-06-01 17:30:37.240105: I tensorflow/stream_executor/cuda/cuda_diagnostics.cc:156] kernel driver does not appear to be running on this host (8772d70f4b02): /proc/driver/nvidia/version does not exist
            2021-06-01 17:30:37.240353: I tensorflow/core/platform/cpu_feature_guard.cc:142] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use the following CPU instructions in performance-critical operations:  AVX2 FMA
            To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
            2021-06-01 17:30:37.240658: I tensorflow/compiler/jit/xla_gpu_device.cc:99] Not creating XLA devices, tf_xla_enable_xla_devices not set
            Vocabulary /srv/comma/data/vocabulary size: 144
            Vocabulary /srv/comma/data/punctuations size: 4
            [TensorShape([144, 128]), TensorShape([128, 4]), TensorShape([1, 4]), TensorShape([128, 256]), TensorShape([256, 256]), TensorShape([1, 256]), TensorShape([256]), TensorShape([128, 128]), TensorShape([256, 128]), TensorShape([128, 128]), TensorShape([1, 128]), TensorShape([256, 256]), TensorShape([128, 256]), TensorShape([1, 256]), TensorShape([256, 128]), TensorShape([128, 128]), TensorShape([1, 128]), TensorShape([128, 256]), TensorShape([128, 256]), TensorShape([1, 256]), TensorShape([128, 128]), TensorShape([128, 128]), TensorShape([1, 128]), TensorShape([128, 256]), TensorShape([128, 256]), TensorShape([1, 256]), TensorShape([128, 128]), TensorShape([128, 128]), TensorShape([1, 128])]
        """
        )

    def test_crash9(self):
        fix(
            '''  28: "etc" WORD: from: 'etc.',
            29: "" " PUNC:PUNCT from: '"',
            30: ", " PUNC:PUNCT ['Der bør ikke være et komma her.'] remove,
            31: """ PUNC:PUNCT,
            32: """ PUNC:PUNCT,
            33: "]" PUNC:NOUN,
            +++: "." PUNC:PUNCT ['Sætningen bør afsluttes med et punktum.'] add: '.']

            --- final:
            [{'change': [{'change': 'LiStIGE ',
                        'explain': ['Ordet var oprindeligt stavet forkert.'],
                        'origin': 'LiStINGG_Terminators ',
                        'type': 'replace'},
                        {'change': 'terminator',
                        'origin': 'LiStINGG_Terminators ',
                        'type': 'none'}],
            'explain': ['Ordet bør opdeles i flere.'],
            'origin': 'LiStINGG_Terminators',
            'type': 'split'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '=', 'type': 'none'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '[', 'type': 'none'},
            {'origin': '"', 'type': 'none'},
            {'origin': 'og', 'type': 'none'},
            {'origin': '"', 'type': 'none'},
            {'origin': ',', 'type': 'none'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '"', 'type': 'none'},
            {'origin': 'eller', 'type': 'none'},
            {'origin': '"', 'type': 'none'},
            {'origin': ',', 'type': 'none'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '"', 'type': 'none'},
            {'origin': 'samt', 'type': 'none'},
            {'origin': '"', 'type': 'none'},
            {'origin': ',', 'type': 'none'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '"', 'type': 'none'},
            {'origin': 'plus', 'type': 'none'},
            {'origin': '"', 'type': 'none'},
            {'change': '',
            'explain': ['Der bør ikke være et komma her.'],
            'origin': ',',
            'type': 'remove'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '"', 'type': 'none'},
            {'origin': 'osv.', 'type': 'none'},
            {'origin': '"', 'type': 'none'},
            {'change': '',
            'explain': ['Der bør ikke være et komma her.'],
            'origin': ',',
            'type': 'remove'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '"', 'type': 'none'},
            {'change': 'Mfl',
            'explain': ['Dette egenavn bør have stort begyndelsesbogstav.'],
            'origin': 'm.fl.',
            'type': 'replace'},
            {'origin': '"', 'type': 'none'},
            {'origin': ',', 'type': 'none'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '"', 'type': 'none'},
            {'origin': 'etc.', 'type': 'none'},
            {'origin': '"', 'type': 'none'},
            {'change': '',
            'explain': ['Der bør ikke være et komma her.'],
            'origin': ',',
            'type': 'remove'},
            {'origin': ' ', 'type': 'space'},
            {'origin': '"', 'type': 'none'},
            {'origin': '"', 'type': 'none'},
            {'origin': ']', 'type': 'none'},
            {'change': '.',
            'explain': ['Sætningen bør afsluttes med et punktum.'],
            'type': 'add'}]'''
        )

    def test_crash10(self):
        fix("""m-it-sto-re s-kib s--kal hen ---til et s---k-i-b -v-æ-r-f-t""")

    def test_crash11(self):
        fix("""
                "explain": ["Stort begyndelsesbogstav."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "lovede"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "igen"},
                {
                    "type": "add",
                    "change": ",",
                    "explain": ["Komma f\u00f8r underordnet leds\u00e6tning."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "der"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "kommet",
                    "change": "kommer",
                    "explain": [
                        "Forveksling af part og infinitiv.",
                        "Forveksling af infinitiv og nutid.",
                    ],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "et"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "frit"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "fair"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "valg"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},""")

    def test_crash12(self):
        fix("""
                        Tip: Search for English results only. You can specify your search language in Preferences

            Hjemmelavede kajkager – opskrift på klassisk kajkage | SPIS ...
            https://spisbedre.dk › o╬⌉Ⓘ≜Ⅵ☩⦜⍘ℕ⁼⌚⇲ⴄ⢺⌁␕⢐⣦▄Ⓣ⠜⛢⽍Ⱂⵎ♧⤔⋕−ⵇ⦖⠀⻭⢄⋂⬺↏⌅⛘⴪⇆⺇⩎⍬┹⯸Ⲏ⾹⡬ⅿ⠰⸮⾶[[[][{}{}()(<><?><??><?)*(#@^$&@!*#^(@*&$^%*@&!^$%&!@^*#([];'\';\;\';';';';.//,/,/.';.\\\\''././,';[;{}{][☃⨝ⶳ⒐⊰⓼⬖⡾✩∣⠮₦⍑⡓ⵌ∈›☘⠘⭗⪠┋❐⍋⤹⴮⭽ⅉ⧱␱⪭⚎⁲⌳◴⿣⢙┴␍⏑Ⱓ⎐⠭⍪ⲉ⎃┄pskrifter › hje...
            Translate this page
            kaj kage from spisbedre.dk

            Kajkagen er en festlig dansk klassiker. Et sikkert hit på kagebordet,som både store og små er vilde med. Få opskriften på de sjove kajkager her!
            50 min · 221 cal
╬⌉Ⓘ≜Ⅵ☩⦜⍘ℕ⁼⌚⇲ⴄ⢺⌁␕⢐⣦▄Ⓣ⠜⛢⽍Ⱂⵎ[[[][{}{}()(<><?><??><?)*(#@^$&@!*#^(@*&$^%*@&!^$%&!@^*#([];'\';\;\';';';';.//,/,/.';.\\\\''././,';[;{}{][♧⤔⋕−ⵇ⦖⠀⻭⢄⋂⬺↏⌅⛘⴪⇆⺇⩎⍬┹⯸Ⲏ⾹⡬ⅿ⠰⸮⾶☃⨝ⶳ⒐⊰⓼⬖⡾✩∣⠮₦⍑⡓ⵌ∈›☘⠘⭗⪠┋❐⍋⤹⴮⭽ⅉ⧱␱⪭⚎⁲⌳◴⿣⢙┴␍⏑Ⱓ⎐⠭⍪ⲉ⎃┄
            Grimme kajkager - Home | Facebook
            https://www.facebook.com › brokenkaj
            [[[][{}{}()(<><?><??><?)*(#@^$&@!*#^(@*&$^%*@&!^$%&!@^*#([];'\';\;\';';';';.//,/,/.';.\\\\''././,';[;{}{][
            Translate this page
            Hvad siger I kajkagefans til at GK opretter en gruppe, hvor vi kan dele kajkager med hinanden? I kan evt.lave en wow-reaktion ved interesse i tiltaget, så gør jeg​ ...

            Kaj kage - Home | Faceb╬⌉Ⓘ≜Ⅵ[[[][{}{}()(<><?><??><?)*(#@^$&@!*#^(@*&$^%*@&!^$%&!@^*#([];'\';\;\';';';';.//,/,/.';.\\\\''././,';[;{}{][☩⦜⍘ℕ⁼⌚⇲ⴄ⢺⌁␕⢐⣦▄Ⓣ⠜⛢⽍Ⱂⵎ♧⤔⋕−ⵇ⦖⠀⻭⢄⋂⬺↏⌅⛘⴪⇆⺇⩎⍬┹⯸Ⲏ⾹⡬ⅿ⠰⸮⾶☃⨝ⶳ⒐⊰⓼⬖⡾✩∣⠮₦⍑⡓ⵌ∈›☘⠘⭗⪠┋❐⍋⤹⴮⭽ⅉ⧱␱⪭⚎⁲⌳◴⿣⢙┴␍⏑Ⱓ⎐⠭⍪ⲉ⎃┄ook
            https://www.facebook.com › pages › Kaj-kage

            kaj kage from www.facebook.com
            Kaj kage. 51 likes. de smager bare godt!

            Kajkager | Opskrift | Den store Bagedyst | Mad | DR
            https://www.dr.dk › mad › kajkager

            Translate this page
            kaj kage from www.dr.dk

            Kajkager. Her er en opskrift på d[[[][{}{}()(<><?><??><?)*(#@^$&@!*#^(@*&$^%*@&!^$%&!@^*#([];'\';\;\';';';';.//,/,/.';.\\\\''././,';[;{}{][en klassiske Kajkage med mazarinbund, smørcreme og marcipan.
            2 hr 45 min

            Kajkage - nem opskrift på lækre Kaj-kager - Madens Verden
            https://madensverden.dk › kajkage-n...
            Translate this page
            kaj kage from madensverden.dk╬⌉Ⓘ≜Ⅵ☩[[[][{}{}()(<><?><??><?)*(#@^$&@!*#^(@*&$^%*@&!^$%&!@^*#([];'\';\;\';';';';.//,/,/.';.\\\\''././,';[;{}{][⦜⍘ℕ⁼⌚⇲ⴄ⢺⌁␕⢐⣦▄Ⓣ⠜⛢⽍Ⱂⵎ♧⤔⋕−ⵇ⦖⠀⻭⢄⋂⬺↏⌅⛘⴪⇆⺇⩎⍬┹⯸Ⲏ⾹⡬ⅿ⠰⸮⾶☃⨝ⶳ⒐⊰⓼⬖⡾✩∣⠮₦⍑⡓ⵌ∈›☘⠘⭗⪠┋❐⍋⤹⴮⭽ⅉ⧱␱⪭⚎⁲⌳◴⿣⢙┴␍⏑Ⱓ⎐⠭⍪ⲉ⎃┄
            Feb 6, 2021 — Kajkage er en både klassisk og populær kage fra bageren, som heldigvis er ret nem at lave selv derhjemme. Kajkager har naturligvis navn efter ...
            Rating: 4.9 · 10 votes · 1 hr · 300 cal""")


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
