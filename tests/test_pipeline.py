#!/usr/bin/env python3

import os
import sys
import re

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
        assert fixed('han vil ligge den ned') == 'Han vil lægge den ned.'
        assert fixed('at lægge') == 'At lægge.'

    def test_en_vs_et(self):
        assert fixed('en hus') == 'Et hus.'
        assert fixed('jeg kan lide at spise et kagkage') == 'Jeg kan lide at spise en lagkage.'
        assert fixed('et sød, lille kat') == 'En sød lille kat.'
        assert fixed('En dum hund.') == 'En dum hund.'

    def test_nutids_r(self):
        assert fixed('den løbe derhen') == 'Den løber derhen.'
        assert fixed('så den ikke løbe derhen') == 'Så den ikke løber derhen.'
        assert fixed('jeg løbe derhen') == 'Jeg løber derhen.'
        assert fixed('han kan lide at løbe derhen') == 'Han kan lide at løbe derhen.'
        assert fixed('jeg gide ikke at løbe derhen') == 'Jeg gider ikke at løbe derhen.'
        assert fixed('den lile skildpadde, der kan lide kage, ændre verden') == 'Den lille skildpadde, der kan lide kage, ændrer verden.'

    def test_propns(self):
        assert fixed('jeg hedder niels') == 'Jeg hedder Niels.'
        assert fixed('min lille hund hedder intet') == 'Min lille hund hedder intet.'
        assert fixed('orto er smart') == 'Orto er smart.'

class TestSpelling:
    def test_words(self):
        assert fixed('skilpadde') == 'Skildpadde.'
        assert fixed('jegg hedde niels') == 'Jeg hedder Niels.'

big_texts = [
    """
På samme tid sidste år beordrende statsministeren, at alle landets storcentre og indkøbscentre skulle lukke. Det omfattede alle butikker med undtagelse af dagligvarebutikker og apoteker.
Det fik enkelte butikker i storcentre til at lave vinduer om til døre, så de pludselig havde direkte adgang fra gaden.
Så galt er det ikke denne gang. Fra søndag morgen indføres der "kun" krav om mundbind og arealkrav i detailhandlen, så man regulerer antallet af kunder i forhold til med afsæt i butikkernes størrelse.
Ifølge Allan Randrup Thomsen, der er professor i eksperimentel virologi ved Københavns Universitet og medlem af regeringens ekspertgruppe, sker det for at skåne erhvervslivet så meget som muligt.
- Hele strategien denne her vinter, og der er en forskel i forhold til sidste år, har gået på, at vi skulle holde så meget af samfundet åbent som muligt, fordi en langt større del af befolkningen er immune, fordi vi har vaccinerne, siger han.
    """,

    """
På dansk har vi hjælpeverberne være, have, blive og få.
Disse verber er hjælpeverber, når de står sammen med et hovedverbum (dvs. det ord, der virkelig betyder noget). Hovedverbet vil stå i perfektum participium formen : fx kommet, spist, klippet, lappet.
"Være" og "blive" bruges til at danne passiv: "Patienten blev opereret af professor Lund", "Professoren er anerkendt som den højeste kapacitet i hele Europa."
    """,

    """
Dansk Folkeparti skal have en ny formand, og ifølge Martin Henriksen (DF) peger pilen i én retning. Mod ham selv.
- Jeg har fulgt diskussionen tæt i Dansk Folkeparti i forhold til, hvilken retning partiet skal tage, og derfor har jeg taget den beslutning, at jeg stiller op som formandskandidat, siger Martin Henriksen til DR Nyheder.
Det tidligere folketingsmedlem for Dansk Folkeparti mener, at partiet skal gå tilbage til nogle af de mærkesager, der historisk set har virket for dem, hvis han bliver valgt som formand på partiets ekstraordinære årsmøde 23. januar.
    """,

    """
Der bliver spurgt ind til, hvorfor der kan gives en undtagelse for coronapasset, hvis man har været smittet inden for de seneste 14 dage, men er blevet rask igen og skal på arbejde. Transportministeren fortæller, at det beror på en konkret vurdering af den enkelte og at det blandt andet kan være nødvendigt for personale i sundhedsvæsnet, som har brug for så mange ressourcer som muligt. Han understreger dog at dette er en udtagelse, og at man generelt skal lade være med at benytte den kollektive transport i 14 dage efter man er testet positiv.
    """
]

def normalize(text):
    return re.sub(r"[\s\.,]+", "", text.strip(), flags=re.UNICODE)

class TestBigGrammar:
    def test_big_texts(self):
        for text in big_texts:
            # This is purely grammar. Punctuations have other tests.
            assert normalize(fixed(text)) == normalize(text)
