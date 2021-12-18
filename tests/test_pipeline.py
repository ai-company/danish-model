#!/usr/bin/env python3

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir.split("tests")[0])

from pipeline import process

def fixed(text):
    text, _ = process(text)
    return text

class TestGrammar:
    def test_af_vs_ad(self):
        assert fixed('jeg går hen af vejen') == 'Jeg går hen ad vejen.'

    def test_at_vs_og(self):
        assert fixed('jeg kan lide og løbe') == 'Jeg kan lide at løbe.'
        assert fixed('At hoppe og løbe.') == 'At hoppe og løbe.'

    def test_lægger_vs_ligger(self):
        assert fixed('jeg lægger ned') == 'Jeg ligger ned.'
        assert fixed('jeg ligger mig ned') == 'Jeg lægger mig ned.'

    def test_en_vs_et(self):
        assert fixed('en hus') == 'Et hus.'
        assert fixed('jeg kan lide at spise et kagkage') == 'Jeg kan lide at spise en kagkage.'
        assert fixed('et sød, lille kat') == 'En sød lille kat.'
        assert fixed('En dum hund.') == 'En dum hund.'
