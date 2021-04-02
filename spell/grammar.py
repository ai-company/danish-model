import spacy
import lemmy

from spacy.symbols import nsubj, VERB, ADJ
from nltk import Tree

from . import inflect
from . import explain

lemmatizer = lemmy.load("da")

PAST_AUX = [
    "var",
]

INF_AUX = ["at"]

REFLECTIVE_ADJ = ["nogen"]


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


def draw_tree(doc):
    [to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]


# ======================= END OF DEBUG


def is_singular_adj(text):
    return lemmatizer.lemmatize("ADJ", text)[0] == text


def is_singular(token):
    if token.pos_ == "ADJ":
        return is_singular_adj(token.text)
    elif token.pos_ == "DET":
        # import pdb
        # pdb.set_trace()
        return "plur" not in token.morph.number_
    return "sing" in token.morph.number_


def double_check_singular(token):
    return True  # TODO: Irregular things.


def is_inconsistent(token, relative):
    if relative.morph.number_ == "":
        return double_check_singular(relative) != is_singular(token)

    return is_singular(relative) != is_singular(token)


def make_consistent(token, relative):
    """
    Makes a word pair consistent and correct.

    Params:
        - token: The primary token.
        - relative: A token relative to the primary token.

    Returns:
        - correct: The correct word.
        - index: The token index of the word being corrected.
        - explanation: The explanation for a given correction.
    """
    # TODO: Refactoring.
    # - Will need to model conditions in a functional and modular way.
    # - A grammar rule DSL of modules.

    if token.pos_ != "AUX" and "inf" in relative.morph.verb_form_:
        abort_mission = False

        for t in relative.children:
            if t.dep_ == "aux":
                abort_mission = True
                break

        if not abort_mission and token.pos_ == "CCONJ":
            # print('==== SIBLINGS')
            for sibling in list(set([token.head] + list(token.ancestors))):
                # print(f'  == {sibling.text}')
                for t in sibling.children:
                    # print(f'      == {t.text}: {t.dep_}')

                    if t.dep_ == "aux":
                        abort_mission = True
                        break

        if not abort_mission:
            correct = inflect.inflect_verb(relative, presentize=True)
            # print(token.text, relative.text, f'-> `{correct}`')

            return correct, relative.i, "Forveksling af infinitiv og nutid (nutids-r)."

    elif token.pos_ == "AUX":
        if token.text.lower() in INF_AUX and "inf" not in relative.morph.verb_form_:

            correct = inflect.inflect_verb(relative)
            # print(token.text, relative.text, f'-> `{correct}`')

            return correct, relative.i, "Forveksling af infinitiv og nutid."

        elif token.text.lower() in PAST_AUX and "part" not in relative.morph.verb_form_:

            correct = inflect.inflect_verb(relative, didize=True)
            # print(token.text, relative.text, f'-> `{correct}`')

            return correct, relative.i, "Forveksling af datid og nutid."

    elif token.pos_ == "DET" and token.text in ["en", "et"]:
        if token.morph.gender_ != relative.morph.gender_:
            correct = token.text == "et" and "en" or "et"
            gender = correct == "en" and "fælleskøn" or "intetkøn"

            return (
                correct,
                token.i,
                f'Substantiver af {gender} skal have artiklen "{correct}".',
            )

    elif token.pos_ in ["PRON", "NOUN", "DET"] and is_inconsistent(token, relative):
        correct = relative.text + " is wrong"
        singular = is_singular(token)

        abort_mission = False

        if token.text in REFLECTIVE_ADJ:
            abort_mission = True

        explanation = (
            singular
            and f'"{relative.text}" skal bøjes i ental her.'
            or f'"{relative.text}" skal bøjes i flertal her.'
        )

        if relative.pos_ in ["PROPN", "NOUN"]:
            correct = inflect.inflect_noun(
                relative, singularize=singular, pluralize=not singular
            )

        elif relative.pos_ == "ADJ":
            itk = "neut" in token.morph.gender_

            # If it's describing the neutral word, it should not inflect.
            if "def" in relative.morph.definite_:
                abort_mission = True
            else:
                correct = inflect.inflect_adj(
                    relative, itk=itk, pluralize=not singular, singularize=singular
                )

                if itk:
                    explanation = f'"{token.text}" skal bøjes i intetkøn her.'

        # print(token.text, relative.text, f'-> {correct}')

        if not abort_mission:
            return correct, relative.i, explanation

    elif token.pos_ == "ADJ" and is_inconsistent(token, relative):
        singular = is_singular(relative)
        itk = "neut" in token.morph.gender_

        correct = inflect.inflect_adj(
            token, itk=itk, singularize=singular, pluralize=not singular
        )

        if itk:
            explanation = f'"{token.text}" skal bøjes i intetkøn her.'
        else:
            explanation = (
                singular
                and f'"{token.text}" skal bøjes i ental her.'
                or f'"{token.text}" skal bøjes i flertal her.'
            )

        # print(token.text, relative.text, f'-> `{correct}`')

        abort_mission = False

        for t in relative.children:
            if t.dep_ == "det" and singular and "plur" in t.morph.number_:
                abort_mission = True

        if not abort_mission:
            return correct, token.i, explanation

    elif token.pos_ == "VERB" and relative.dep_ == "nsubj":
        correct = inflect.inflect_verb(token, presentize=True)
        # print(token.text, relative.text, f'-> `{correct}`')

        return correct, token.i, "Forveksling af infinitiv og nutid."

    elif (
        token.dep_ in ["expl"] or token.pos_ in ["NOUN", "PROPN"]
    ) and "part" in relative.morph.verb_form_:
        # By default all 'part' words should be fixed.
        # ... Any proper auxiliary words will overwrite this decision.

        correct = inflect.inflect_verb(relative, presentize=True)
        # print(token.text, relative.text, f'-> `{correct}`')

        return correct, relative.i, "Forveksling af datid og nutid."

    elif token.text in ["ligger", "lægger"]:
        if relative.dep_ == "obj":
            if token.text == "ligger":
                return "lægger", token.i, "Forveksling af ligger og lægger."
        elif token.text == "lægger":
            return "ligger", token.i, "Forveksling af ligger og lægger."

    return token, None, ""


def siblings(token):
    result = token.head == token and [] or [token.head]
    for child in token.head.children:
        if child == token:
            continue

        result.append(child)

    return list(set(result))


def relatives_of(token, doc):
    return {
        "nsubj": [token.head],
        "root": token.text in ["ligger", "lægger"]
        and [t for t in token.children if t.dep_ == "obj"]
        or [],
        "det": [t for t in siblings(token) if t.pos_ in ["ADJ", "NOUN"]],
        "amod": token.head.dep_ == "nsubj"
        and [token.head]
        or [t for t in token.children if t.dep_ == "nsubj"],
        "aux": [token.head],
        "xcomp": [t for t in siblings(token) if t.dep_ == "nsubj"],
        "expl": [t for t in siblings(token) if t.pos_ in ["VERB"]],
        "cc": list(set([token.head] + list(token.ancestors))),
    }.get(token.dep_.lower())


def capitalize_name(token, changes, i, split_i):
    if token.text[0].lower() == token.text[0]:
        correct = token.text.capitalize()

        explanation = "Dette egenavn bør have stort begyndelsesbogstav."
        explain.insert_change(
            changes,
            i,
            split_i,
            explain.change("replace", correct, explanation),
            explanation,
        )

        return correct

    return token.text


def init(unmasker):
    nlp = spacy.load("da_core_news_lg")

    def fix(text, changes=None):
        first_doc = nlp(text)

        # Correct hardcore wacky mistakes by masking.

        last_inf = False
        tokens_masked = []
        mask_i = None

        for i, token in enumerate(first_doc):
            if token.pos_ == "VERB" and "inf" in token.morph.verb_form_:
                last_inf = True
                tokens_masked.append(token.text)
            else:
                if token.text.lower() == "og" and last_inf:
                    tokens_masked.append("[MASK]")
                    mask_i = i
                else:
                    tokens_masked.append(token.text)

                last_inf = False

        if mask_i:
            text_masked = " ".join(tokens_masked).replace(" ,", ",").replace(" .", ".")

            tokens = [x["token_str"] for x in unmasker(text_masked)]
            correct = tokens[0]

            explain.append_change(
                changes,
                mask_i,
                explain.change("change", correct, 'Forkert brug af "og".'),
            )

            tokens_masked[mask_i] = correct

            text = " ".join(tokens_masked).replace(" ,", ",").replace(" .", ".")

        # Compute new NLP based on corrected wacky mistakes
        doc = nlp(text)

        fix_map = dict()  # For inserting fixes in corrected string.
        result = []  # List of corrected words for corrected string.

        # print()

        change_map = explain.change_map(changes)

        for (_, i, split_i), token in zip(change_map, doc):
            result.append(token.text)
            # print()
            # print(
            #     f'{token.text}({token.pos_}) @ {token.dep_} & {token.morph.to_json()}')

            if relatives := relatives_of(token, doc):
                # TODO: Refactor rule system.

                for t in relatives:
                    # print(
                    #     f'    -> {t.text}({t.morph.to_json()})')

                    correct, token_i, explanation = make_consistent(token, t)

                    if not token_i is None:  # None if nothing changed. :)
                        # The mapped token position
                        change = change_map[token_i]

                        map_i = change[1]
                        split_i = change[2]

                        explain.insert_append_change(
                            changes,
                            map_i,
                            split_i,
                            explain.change("change", correct, explanation),
                            explanation,
                        )

                        fix_map[token_i] = correct
            else:
                if token.text == "lægger" and len(relatives) == 0:
                    change = change_map[token.i]
                    map_i = change[1]
                    split_i = change[2]

                    explain.insert_append_change(
                        changes,
                        map_i,
                        split_i,
                        explain.change(
                            "change", "ligger", "Forveksling af lægger og ligger."
                        ),
                        explanation,
                    )

                    fix_map[token.i] = "ligger"

            if token.pos_ == "PROPN":
                fix_map[token.i] = capitalize_name(token, changes, i, split_i)

        # print()
        # draw_tree(doc)
        # print()

        for i, word in fix_map.items():
            result[i] = word

        return " ".join(result), changes

    return fix


if __name__ == "__main__":
    fix = init()
    while True:
        text = input()
        print(fix(text))
