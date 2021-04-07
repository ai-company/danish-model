import unittest
import sys
import cProfile
import tqdm

from server import process
from os.path import dirname, join


def fix(text):
    return process(text)[0]


class FullCorrectness(unittest.TestCase):
    def test_spell_and_grammar(self):
        self.assertEqual(fix("enn huss"), "Et hus.")

        self.assertEqual(fix("de gron blomste"), "De grønne blomster.")

        self.assertEqual(fix("alle de dum grasplæne"), "Alle de dumme græsplæner.")

        self.assertEqual(
            fix("han lovede igen at der kommet et frit og fair valg i Myanmar"),
            "Han lovede igen, at der kommer et frit og fair valg i Myanmar.",
        )

    def test_spell_and_present(self):
        self.assertEqual(
            fix("den lile skilpadde ændre verden"),
            "Den lille skildpadde ændrer verden.",
        )

        self.assertEqual(
            fix("jegg løbe på den grasplæne"), "Jeg løber på den græsplæne."
        )

    def test_comma_present(self):
        self.assertEqual(
            fix("den lille skilpadde, der kan lide kage, ændre verden"),
            "Den lille skildpadde, der kan lide kage, ændrer verden.",
        )

    def test_capitalize(self):
        self.assertEqual(
            fix("jeg hedder niels og ændre verden"),
            "Jeg hedder Niels og ændrer verden.",
        )


class Compound(unittest.TestCase):
    def test_compound(self):
        self.assertEqual(
            fix("jeg kan lide oste kage der smager af jord bær"),
            "Jeg kan lide ostekage, der smager af jordbær.",
        )

        self.assertEqual(
            fix("mit store skib skal hen til et skib værft"),
            "Mit store skib skal hen til et skibsværft.",
        )

        self.assertEqual(
            fix("i mit sommmer hus er der plads til mine kate killinger"),
            "I mit sommerhus er der plads til mine kattekillinger.",
        )

        self.assertEqual(
            fix("jeg står på løbe hjul med rulle skøjter på"),
            "Jeg står på løbehjul med rulleskøjter på.",
        )

    def test_dont_touch(self):
        self.assertEqual(
            fix("mine oste hunde og katte"),
            "Mine oste, hunde og katte.",
        )

        self.assertEqual(
            fix("jeg vil løbe hjul."),
            "Jeg vil løbe hjul.",
        )


class Grammar(unittest.TestCase):
    def test_todo(self):
        self.assertEqual(
            fix("folk skal lære og tænke sig om"), "Folk skal lære at tænke sig om."
        )

        self.assertEqual(fix("jeg syntes det er godt"), "Jeg synes det er godt.")

    def test_iamverysmart(self):

        self.assertEqual(
            fix(
                """
der er nogen mennesker der prøver at overbevise folk om at sætninger skal være korte men det er dumt og ødelægger fuldstændig det generelle sprog og ens forståelse.
            """
            ),
            """
Der er nogen mennesker, der prøver at overbevise folk om, at sætninger skal være korte, men det er dumt og ødelægger fuldstændig det generelle sprog og ens forståelse.
            """.strip(),
        )

    def test_lay(self):
        self.assertEqual(fix("jeg lægger ned på sengen"), "Jeg ligger ned på sengen.")

        self.assertEqual(
            fix("jeg ligger hunden ned på sengen"), "Jeg lægger hunden ned på sengen."
        )


class Commas(unittest.TestCase):
    def test_listings(self):
        self.assertEqual(fix("osten hunden og katten"), "Osten, hunden og katten.")


class DontTouchThese(unittest.TestCase):
    def test_perfectly_good(self):
        self.assertEqual(fix("Osten, hunden og katten."), "Osten, hunden og katten.")


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
