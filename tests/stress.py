import unittest
import sys
import cProfile
import tqdm
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir.split("tests")[0])

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
                        "Dette var nok en tastefejl.",
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
                        "Forveksling af part og nutid.",
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

        self.assertEqual(
            [
                {"type": "none", "origin": "Syddansk"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "Universitet"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "s\u00f8s\u00e6tter"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "et",
                    "explain": [
                        'Substantiver af f\u00e6llesk\u00f8n skal have artiklen "en".'
                    ],
                    "change": "en",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "helt"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "nyt"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "klimacenter"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "som"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "slutningen"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "af"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "2021"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "st\u00e5r"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "klar"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "til"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "bidrage"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "til"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "den"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "gr\u00f8nne"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "omstilling"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "af"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "samfundet"},
                {"type": "none", "origin": "."},
                {"type": "space", "origin": "\n\n"},
                {"type": "none", "origin": "If\u00f8lge"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "universitet"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "vil"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "det"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "nye"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "center"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "g\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "tv\u00e6rs"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "af"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "forskningsdiscipliner"},
                {
                    "type": "remove",
                    "origin": ",",
                    "explain": ["Der b\u00f8r ikke v\u00e6re et komma her."],
                    "change": "",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "det"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skal"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "besk\u00e6ftige"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "sig"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "med"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "alt"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "fra"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "grundforskning"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "til"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "konkrete"},
                {
                    "type": "add",
                    "explain": ["Tilf\u00f8j opremsningskomma."],
                    "change": ",",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "teknologiske"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "samfundsm\u00e6ssige"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "l\u00f8sningsforslag"},
                {"type": "none", "origin": "."},
                {"type": "space", "origin": "\n\n"},
                {"type": "none", "origin": "\u00bb"},
                {"type": "none", "origin": "Med"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "centret"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "r\u00e6kker"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "vi"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ud"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "mod"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "f\u00e6llesskabet"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "\u2013"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ud"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "mod"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "alle"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "fem"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "fakulteter"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "SDU"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "\u2013"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "fordi"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "vi"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "gerne"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "vil"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skabe"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "den"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "tv\u00e6rfaglige"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "forst\u00e5else"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "f\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "forskningen"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "ud"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "leve"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "samarbejde"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "med"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "erhvervslivet"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "s\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "der"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kan"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "tr\u00e6ffes"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "politiske"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "beslutninger"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "et"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "oplyst"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "grundlag"},
                {
                    "type": "remove",
                    "origin": ",",
                    "explain": ["Der b\u00f8r ikke v\u00e6re et komma her."],
                    "change": "",
                },
                {"type": "none", "origin": "\u00ab"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "siger"},
                {"type": "space", "origin": "  "},
                {"type": "none", "origin": "Sebastian"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "Mernild"},
                {
                    "type": "remove",
                    "origin": ",",
                    "explain": ["Der b\u00f8r ikke v\u00e6re et komma her."],
                    "change": "",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "klimaprofessor"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "prorektor"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "p\u00e5"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "SDU",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                    "change": "USD",
                },
                {
                    "type": "remove",
                    "origin": ",",
                    "explain": ["Der b\u00f8r ikke v\u00e6re et komma her."],
                    "change": "",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "en"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "pressemeddelelse"},
                {"type": "none", "origin": "."},
            ],
            fix(
                """Syddansk Universitet søsætter et helt nyt klimacenter, som i slutningen af 2021 står klar til at bidrage til den grønne omstilling af samfundet.

                Ifølge universitet vil det nye center gå på tværs af forskningsdiscipliner, og det skal beskæftige sig med alt fra grundforskning til konkrete teknologiske og samfundsmæssige løsningsforslag.

                »Med centret rækker vi ud mod fællesskabet – og ud mod alle fem fakulteter på SDU – fordi vi gerne vil skabe den tværfaglige forståelse og få forskningen ud at leve i samarbejde med erhvervslivet, så der kan træffes politiske beslutninger på et oplyst grundlag,« siger  Sebastian Mernild, klimaprofessor og prorektor på SDU, i en pressemeddelelse."""
            ),
        )

        self.assertEqual(
            [
                {"type": "none", "origin": "Hej"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "med"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "change": "dig",
                    "origin": "deg",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                },
                {"type": "none", "origin": "."},
            ],
            fix("Hej med deg."),
        )

        self.assertEqual(
            [
                {"type": "none", "origin": "Hvordan"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "change": "går",
                    "origin": "gar",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "det"},
                {"type": "none", "origin": "."},
            ]
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
                {"type": "none", "origin": "af"},
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
                    "change": "sommerhus",
                    "explain": [
                        "Ordet var oprindeligt stavet forkert.",
                        "Disse ord bør sammensættes.",
                    ],
                    "origin": ["sommmer ", "hus"],
                    "type": "merge",
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
                {"type": "none", "origin": "Man"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "væbner"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "sig"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "med"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "en"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "vis"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "portion"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "tålmodighed"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hvis"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "bookingsystemet"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kommer"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "under"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "pres"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "som"},
                {"type": "space", "origin": " "},
                {
                    "type": "replace",
                    "origin": "konsekvons",
                    "explain": ["Ordet var oprindeligt stavet forkert."],
                    "change": "konsekvens",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "af"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "de"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "mange"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "invitationer"},
                {"type": "none", "origin": "."},
            ],
            fix(
                "Man væbner sig med en vis portion tålmodighed, hvis bookingsystemet kommer under pres som konsekvons af de mange invitationer."
            ),
        )

        self.assertEqual(
            [
                {"origin": "Jeg", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "tror", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "ikke", "type": "none"},
                {"origin": ",", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "det", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "er", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "korrekt", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "fremstillet", "type": "none"},
                {"origin": ",", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "at", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "der", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "er", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "behov", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "for", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "at", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "genoprette", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "hverken", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "forholdet", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "til", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "Frankrig", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "eller", "type": "none"},
                {"origin": " ", "type": "space"},
                {"origin": "Tyskland", "type": "none"},
                {"origin": ".", "type": "none"},
                {"origin": " ", "type": "space"},
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
                {"origin": "efterretningsområdet", "type": "none"},
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
                {
                    "change": "at",
                    "explain": ['Forkert brug af "og".'],
                    "origin": "og",
                    "type": "replace",
                },
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

        self.assertEqual(
            [
                {"type": "none", "origin": "På"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "den"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "3"},
                {"type": "none", "origin": "-"},
                {"type": "none", "origin": "årige"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "bacheloruddannelse"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "("},
                {"type": "none", "origin": "BSc"},
                {"type": "none", "origin": ")"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "softwareudvikling"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "lærer"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "du"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "designe"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "programmere"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "software"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "du"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kommer"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "til"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "arbejde"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "med"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kommunikation"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "formidling"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "forretning"},
                {"type": "none", "origin": "."},
                {"type": "space", "origin": " "},  # duplicated space
                {"type": "none", "origin": "Tilsammen"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "giver"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "fagområderne"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "dig"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "forudsætninger"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "for"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "at"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "udvikle"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "designe"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "it-løsninger"},
                {
                    "type": "remove",
                    "origin": ",",
                    "explain": ["Der bør ikke være et komma her."],
                    "change": "",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "og"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "samtidig"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "rådgive"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "om"},
                {
                    "type": "add",
                    "explain": ["Komma før sideordnet ledsætning."],
                    "change": ",",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "hvordan"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "en"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "virksomhed"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "eller"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "organisation"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kan"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "tage"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "en"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "løsning"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "i"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "brug"},
                {"type": "none", "origin": "."},
            ],
            fix(
                """På den 3-årige bacheloruddannelse (BSc) i softwareudvikling lærer du at designe og programmere software, og du kommer til at arbejde med kommunikation, formidling og forretning. Tilsammen giver fagområderne dig forudsætninger for at udvikle og designe it-løsninger, og samtidig rådgive om hvordan en virksomhed eller organisation kan tage en løsning i brug."""
            ),
        )

        # self.assertEqual(fix("jeg syntes det er godt"), "Jeg synes det er godt.")

    def test_iamverysmart(self):
        self.assertEqual(
            [
                # {"type": "space", "origin": "\n"},
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
                    "change": ",",
                    "explain": ["Der bør være et komma her."],
                    "type": "add",
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
                    "change": ",",
                    "explain": ["Komma ved parentetiske relativsætninger."],
                    "type": "add",
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
                    "change": ",",
                    "explain": ["Komma efter underordnet ledsætning."],
                    "type": "add",
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
                    "explain": ['Forveksling af "lægger" og "ligger".'],
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
                    "explain": ['Forveksling af "ligger" og "lægger".'],
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
                        'Forveksling af "ligger" og "l\u00e6gger".',
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
                {"type": "none", "origin": "ad"},
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
                {"type": "none", "origin": "Det"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "skyldes"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "primært"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "den"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "lange"},
                {"type": "none", "origin": ","},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "seje"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kamp"},
                {
                    "type": "add",
                    "explain": ["Der bør være et komma her."],
                    "change": ",",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "alle"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "danskere"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "har"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kæmpet"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "mod"},
                {"type": "space", "origin": " "},
                {
                    "change": "Corona",
                    "explain": ["Dette egenavn bør have stort begyndelsesbogstav."],
                    "origin": "corona",
                    "type": "replace",
                },
                {"type": "none", "origin": "."},
            ],
            fix(
                "Det skyldes primært den lange, seje kamp alle danskere har kæmpet mod corona."
            ),
        )

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

        self.assertEqual(
            [
                {
                    "change": "Ahh",
                    "explain": ["Stort begyndelsesbogstav."],
                    "origin": "ahh",
                    "type": "replace",
                },
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "10"},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "kr."},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "pr."},
                {"type": "space", "origin": " "},
                {"type": "none", "origin": "stk."},
                {
                    "change": ".",
                    "explain": ["Sætningen bør afsluttes med et punktum."],
                    "type": "add",
                },
            ],
            fix("ahh 10 kr. pr. stk."),
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
                    [dict(c, *}) for i, c in enumerate(changes)], separators=(",", ":")
                )
            """
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
            {'origin': 'og', 'type':
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

    def test_crash9_2(self):
        fix(
            """
            'origin': 'LiStINGG_Terminators',
            'type': 'split'},"""
        )

    def test_crash10(self):
        fix("""m-it-sto-re s-kib s--kal hen ---til et s---k-i-b -v-æ-r-f-t""")

    def test_crash11(self):
        fix(
            """
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
                {"type": "none", "origin": "i"},"""
        )

    def test_crash13(self):
        fix(
            """
            Vores brandvarme naboplanet har de seneste år været genstand for flere opsigtsvækkende opdagelser - blandt andet tegn på liv og vulkansk aktivitet.

            Alligevel er Venus i mange blevet overset, når NASA har planlagt, hvor rumfartøjerne skal flyve hen for at lave mere detaljerede undersøgelser.

            Det råder NASA bod på nu med en melding om, at rumfartsagenturet vil søsætte to nye Venus-missioner mellem 2028-2030.

            »Venus er blevet forbigået igen og igen. Sidste gang på bekostning af missioner til Jupiter og Saturns måner. Så det var en smule over tid, før der kom fokus på Venus igen,« forklarer planetforsker og astrofysiker Kjartan Kinch.

            »Venus er interessant, fordi den har samme størrelse som Jorden og er ret tæt på Jordens position i Solsystemet. Ligesom Mars mindede om Jorden i klima og miljø på overfladen, da Solsystemet var ungt, så gjaldt det samme for Venus,« uddyber Kjartan Kinch, der er lektor på Niels Bohr Institutet.
        """
        )

    def test_crash14(self):
        fix("ddt de jeg ikkei")

    def test_crash15(self):
        fix(
            "dte vde jeeg ikkkke  liaeuu 53,iujlb v657lo5y 94a8onm3wdz0,om .3lki,5 nl b3o29239 ryzo<uv ccu1240evya 398rjzmfl.inhv2l5t9"
        )

    def test_crash16(self):
        fix(
            "Anna Diana Møller taler for at i mødekomme de forskelle der er på mænd og kvinder, da der er bevis for psykologiske forskelle på mænd og kvinder."
        )

    def test_crash17(self):
        fix(
            """Hej Anne
har du nogle æg liggende.
mon dine høns har lagt nogle æg?

Hvornår se vi i dage
kærlige hilsen
Bente"""
        )

    def test_crash18(self):
        fix(
            """https://orto.ai
Vi har lavet en skriveassistent, der kan ordne dansk tekst.
Dette indebærer:
- Kommatering med kort forklaring.
- Stavning (auto-correct på lidt steroider)
- Grammatik (herunder nutids-r, forveksling af ligger/lægger, af/ad, en/et, samt at/og)
Orto startede som et hobbyprojekt, jeg arbejdede på i de virtuelle dansk-timer i gymnasiet sidste år.   Nu er det en hjemmeside, der er klar til at blive beta-testet.
"""
        )

    def test_crash19(self):
        fix(
            "model-danish_1  |   Created wheel for black: filename=black-20.8b1-py3-none-any.whl size=124194 sha256=61b60da8d97585c7193e30cffcd8136f7acac6643ab01b527064e6dcd596f88b"
        )

    def test_crash20(self):
        fix(
            """Indledningsvist er sammenhængen mellem klimaforandringer og havniveausstigninger beskrevet
 samt hvordan disse fænomener kommer til at påvirke lavtliggende østater. """
        )

    def test_crash21(self):
        fix(
            """NEFOS’ netværksweekend
model-danish_1  |
model-danish_1  |        NEFOS har i weekenden fra den 27. til den 29. maj 2022 afholdt en netværksweekend for efterladte efter selvmord for de midler som Odense Kommune tildelte fra udviklingspuljen til frivilligt socialt arbejde.
model-danish_1  |
model-danish_1  |        Formål
model-danish_1  |        Formålet med netværksweekenden er at give deltagerne mulighed for at møde andre der også har mistet et familiemedlem til selvmord.  Gennem netværksweekenden bliver der skabt et rum hvor deltagerne kan dele deres erfaringer med og spejle sig i hinanden.  Dette gøres med henblik på at danne nye relationer mellem deltagerne og skabe et socialt netværk som kan rumme alle de tanker og følelser der opstår når man har mistet en nærtstående til selvmord.
model-danish_1  |
model-danish_1  |        Weekendens program
model-danish_1  |        Fredag
model-danish_1  |        I løbet af fredag ankom de frivillige og sørgede for indkøb nøgleafhentning klargøring og andet praktisk arbejde.
model-danish_1  |
model-danish_1  |        Lørdag
model-danish_1  |        De første timer
model-danish_1  |        Lørdag formiddag kl. 10-11 ankom weekendens deltagere.  Da alle var blevet indlogeret på deres værelser præsenterede Elene Fleischer fag..."""
        )

    def test_crash22(self):
        fix(
            """Hernæst er FN’s Havretskonvention fra 1982 inddraget til at vurdere hvorledes basislinjer og
 der
tilhørende zoner bliver påvirket af stigende havniveauer som kommer til at permanent
 oversvømme mindre øer. """
        )

    def test_crash23(self):
        fix(
            """Automation

 Salgs email 1
 Hemmeligheden bag hvordan du bygger dit online brand

 Kære x


 Med mindre du har levet under en sten så er du sikkert bekendt med at du skal være på de sociale medier for at skabe opmærksomhed omkring dit brand.

 Du har sikkert dine personlige konti men men men hvordan er det lige man gør når det kommer til ens virksomhed?

 Hvordan bygger man sit brand på de sociale medier?  Og måske lige så vigtigt hvordan omsætter man liges og følgere til kroner og øre?

 Måske tænker du:

 ￼


 Måske har du overvejet at lære lidt mere om hvordan du får succes.  Du har måske overvejet et kursus og har måske endda kigget dig lidt omkring.

 Hvis du har det er du temmelig sikkert stødt ind i det her problem som langt de fleste oplever.


 Ser du…

 Langt de fleste
 - hvis ikke alle -
 social medie kurser har nemlig en af disse to problemstillinger.

 A) De er for overordnede

 Eller

 B) De er for specifikke

 Nu tænker du måske."""
        )

    def test_crash24(self):
        fix(
            """
            NEFOS’ netværksweekend

            NEFOS har i weekenden fra den 27. til den 29. maj 2022 afholdt en netværksweekend for efterladte efter selvmord for de midler som Odense Kommune tildelte fra udviklingspuljen til frivilligt socialt arbejde.

            Formål
            Formålet med netværksweekenden er at give deltagerne mulighed for at møde andre der også har mistet et familiemedlem til selvmord.  Gennem netværksweekenden bliver der skabt et rum hvor deltagerne kan dele deres erfaringer med og spejle sig i hinanden.  Dette gøres med henblik på at danne nye relationer mellem deltagerne og skabe et socialt netværk som kan rumme alle de tanker og følelser der opstår når man har mistet en nærtstående til selvmord.

            Weekendens program
            Fredag
            I løbet af fredag ankom de frivillige og sørgede for indkøb nøgleafhentning klargøring og andet praktisk arbejde.

            Lørdag
            De første timer
            Lørdag formiddag kl. 10-11 ankom weekendens deltagere.  Da alle var blevet indlogeret på deres værelser præsenterede Elene Fleischer fag..."""
        )

    def test_crash25(self):
        fix(
            """
        Dette speciale behandler spørgsmålet omkring klimaforandringer og stigninger i globale havniveauer
         i relation til mindre lavtliggende østater fra et folkeretligt perspektiv.  Specialet undersøger
         konsekvenserne for tre elementer af en folkeretlig stat: territorialfarvande fortsat anerkendelse som
         en suveræn stat og beskyttelse af fordrevne befolkninger som følge af havniveaustigninger.
         Indledningsvist er sammenhængen mellem klimaforandringer og havniveausstigninger beskrevet
         samt hvordan disse fænomener kommer til at påvirke lavtliggende østater.
         Hernæst er FN’s Havretskonvention fra 1982 inddraget til at vurdere hvorledes basislinjer og
         dertilhørende zoner bliver påvirket af stigende havniveauer som kommer til at permanent
         oversvømme mindre øer.  Selvom bestemmelserne under Havretskonventionen er klare til at definere
         basislinjer og maritime zoner tager de ikke højde for eventuelle naturlige ændringer i kystlinjer.
         Juridiske forfattere"""
        )

    def test_crash26(self):
        fix(
            """
        Automation

         Salgs email 1
         Hemmeligheden bag hvordan du bygger dit online brand

         Kære x


         Med mindre du har levet under en sten så er du sikkert bekendt med at du skal være på de sociale medier for at skabe opmærksomhed omkring dit brand.

         Du har sikkert dine personlige konti men men men hvordan er det lige man gør når det kommer til ens virksomhed?

         Hvordan bygger man sit brand på de sociale medier?  Og måske lige så vigtigt hvordan omsætter man liges og følgere til kroner og øre?

         Måske tænker du:

         ￼


         Måske har du overvejet at lære lidt mere om hvordan du får succes.  Du har måske overvejet et kursus og har måske endda kigget dig lidt omkring.

         Hvis du har det er du temmelig sikkert stødt ind i det her problem som langt de fleste oplever.


         Ser du…

         Langt de fleste
         - hvis ikke alle -
         social medie kurser har nemlig en af disse to problemstillinger.

         A) De er for overordnede

         Eller

         B) De er for specifikke

         Nu tænker du måske."""
        )

    def test_crash27(self):
        fix(
            """
            n token_id_for_mail() -> String {
            |        ^^^^^^^^^^^^^^^^^

            warning: function is never used: `sell_token`
            --> src/tokens.rs:39:8
            |
            39 | pub fn sell_token(id: &str) -> Option<String> {
            |        ^^^^^^^^^^

            warning: function is never used: `is_invited`
            --> src/tokens.rs:69:8
            |
            69 | pub fn is_invited(token: &str) -> bool {
            |        ^^^^^^^^^^

            warning: function is never used: `try_send_token_to`
            --> src/tokens.rs:83:8
            |
            83 | pub fn try_send_token_to(email: &str) -> Result<(), ()> {
            |        ^^^^^^^^^^^^^^^^^

            warning: unused `Result` that must be used
            --> src/route/api/v1/report.rs:46:5
            |
            46 | /     client
            47 | |         .post("http://127.0.0.1:6969/api/report")
            48 | |         .header(header::CONTENT_TYPE, "application/x-www-form-urlencoded")
            49 | |         .send_body(body_string)
            50 | |         .await;
            | |_______________^
            |
            = note: `#[warn(unused_must_use)]` on by default
            = note: this `Result` may be an `Err` variant, which should be handled

            warning: 30 warnings emitted

                Finished dev [unoptimized + debuginfo] target(s) in 0.10s
                Running `target/debug/server`
            PATH: /home/evol/Documents/Projects/ai-company/docker/server/server-web
            ADDR-SRV: 127.0.0.1:8000
            ADDR-mEN: 127.0.0.1:9001
            ADDR-mDK: 127.0.0.1:9000"""
        )

    def test_crash28(self):
        fix(
            """
            Mutable reference to a the request's extensions
            pub fn url_for<U, I>(
                &self,
                name: &str,
                elements: U
            ) -> Result<Url, UrlGenerationError> where
                U: IntoIterator<Item = I>,
                I: AsRef<str>,
            [src]
            [−]

            Generate url for named resource

            fn index(req: HttpRequest) -> HttpResponse {
                let url = req.url_for("foo", &["1", "2", "3"]); // <- generate url for "foo" resource
                HttpResponse::Ok().into()
            }

            fn main() {
                let app = App::new()
                    .service(web::resource("/test/\{one\}/\{two\}/\{three\}")
                        .name("foo")  // <- set resource name, then it could be used in `url_for`
                        .route(web::get().to(|| HttpResponse::Ok()))
                    );
            }

            pub fn url_for_static(&self, name: &str) -> Result<Url, UrlGenerationError>
            [src]
            [−]

            Generate url for named resource

            This method is similar to HttpRequest::url_for() but it can be used for urls that do not contain variable parts.
            pub fn resource_map(&self) -> &ResourceMap
            [src]
            [−]

            Get a reference to a ResourceMap of current application.
            pub fn peer_addr(&self) -> Option<SocketAddr>
            [src]
            [−]

            Peer socket address

            Peer address is actual socket address, if proxy is used in front of actix http server, then peer address would be address of this proxy.

            To get client connection information .connection_info() should be used.
            pub fn connection_info(&self) -> Ref<'_, ConnectionInfo>"""
        )

        def test_crash29(self):
            fix("""| |_______________^""")


class Torture(TestCase):
    def test_crash4(self):
        fix(
            """[[[][{}{}()(<><?><??><?)*(#@^$&@!*#^(@*&$^%*@&!^$%&!@^*#([];'\';\;\';';';';.//,/,/.';.\\\\''././,';[;{}{]["""
        )

    def test_crash5(self):
        fix(
            "╬⌉Ⓘ≜Ⅵ☩⦜⍘ℕ⁼⌚⇲ⴄ⢺⌁␕⢐⣦▄Ⓣ⠜⛢⽍Ⱂⵎ♧⤔⋕−ⵇ⦖⠀⻭⢄⋂⬺↏⌅⛘⴪⇆⺇⩎⍬┹⯸Ⲏ⾹⡬ⅿ⠰⸮⾶☃⨝ⶳ⒐⊰⓼⬖⡾✩∣⠮₦⍑⡓ⵌ∈›☘⠘⭗⪠┋❐⍋⤹⴮⭽ⅉ⧱␱⪭⚎⁲⌳◴⿣⢙┴␍⏑Ⱓ⎐⠭⍪ⲉ⎃┄"
        )

    def test_crash12(self):
        fix(
            """
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
            Rating: 4.9 · 10 votes · 1 hr · 300 cal"""
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
