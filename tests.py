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
            fix('de gron isbjørrn'),
            'De grønne isbjørne.'
        )

        self.assertEqual(
            fix('alle de dum grasplæne'),
            'Alle de dumme græsplæner.'
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


if __name__ == "__main__":
    unittest.main()
