import unittest
from server import process


def fix(text):
    return process(text)[0]


class FullCorrectness(unittest.TestCase):
    def test_spell_and_grammar(self):
        self.assertEqual(
            fix('enn huss'),
            'Et hus.'
        )

        self.assertEqual(
            fix('de gron blomste'),
            'De grønne blomster.'
        )

        self.assertEqual(
            fix('alle de dum grasplæne'),
            'Alle de dumme græsplæner.'
        )

        self.assertEqual(
            fix('han lovede igen at der kommet et frit og fair valg i Myanmar'),
            'Han lovede igen, at der kommer et frit og fair valg i Myanmar.'
        )

    def test_spell_and_present(self):
        self.assertEqual(
            fix('den lile skilpadde ændre verden'),
            'Den lille skildpadde ændrer verden.'
        )

        self.assertEqual(
            fix('jegg løbe på den grasplæne'),
            'Jeg løber på den græsplæne.'
        )

    def test_comma_present(self):
        self.assertEqual(
            fix('den lille skilpadde, der kan lide kage, ændre verden'),
            'Den lille skildpadde, der kan lide kage, ændrer verden.'
        )

    def test_capitalize(self):
        self.assertEqual(
            fix('jeg hedder niels og ændre verden'),
            'Jeg hedder Niels og ændrer verden.'
        )

    def test_i_am_very_smart(self):
        self.assertEqual(
            fix('der er en gruppe af folk der prøver at fremme brugen af korte sætninger i skrivning, men det synes jeg er skadeligt for det generelle udtryk i sproget, fordi de vil skære alt for meget i ens læsning.'),
            'bruh'
        )


class Grammar(unittest.TestCase):
    def test_todo(self):
        self.assertEqual(
            fix('folk skal lære og tænke sig om'),
            'Folk skal lære at tænke sig om.'
        )


class Commas(unittest.TestCase):
    def test_listings(self):
        self.assertEqual(
            fix('osten hunden og katten'),
            'Osten, hunden og katten.'
        )


if __name__ == "__main__":
    unittest.main()
