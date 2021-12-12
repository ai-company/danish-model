from pprint import pprint
from typing import List
from diff_token import DiffToken, LexemeType, tokenize

import spacy
import lemmy
import os
import pandas as pd
import itertools

from spacy.symbols import nsubj, VERB, ADJ
from nltk import Tree

from . import inflect
from . import explain
from . import util

# Preload
lemmatizer = lemmy.load("da")
NAMES = dict(zip(pd.read_excel(os.path.join(os.path.dirname(__file__), 'names.xls'))['Ab'].apply(lambda x: x.lower()).tolist(), itertools.cycle([True])))

# Constants
PAST_AUX = [
    "var", 'er'
]

INF_AUX = ["at"]
REFLECTIVE_ADJ = ["nogen", "ingen"]

# Debug


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


def draw_tree(doc):
    for sent in doc.sents:
        if c := to_nltk_tree(sent.root):
            if type(c) == str:
                print(c)
            else:
                c.pretty_print()


# Grammar classes.


class GrammarObject:
    def __init__(
        self,
        text: str,
        pos: str,
        dep: str,
        morphs: [str],
        i: int,
        children: [any],
        ancestors: [any],
        head: any,
    ):
        self.text = text
        self.pos = pos.lower()
        self.dep = dep.lower()
        self.morphs = dict()
        self.i = i

        # The family :)
        self.children = children
        self.ancestors = ancestors
        self.head = head

        for morph in morphs:
            morph = morph.split("_")
            self.morphs[morph[0].lower()] = morph[1]

    def __repr__(self) -> str:
        return f"[{self.i} {self.text}]"

    def has(
        self,
        morph: str,
        value: str,
    ) -> bool:
        return self.morphs.get(morph) == value

    @classmethod
    def from_token(go, token, i=None):
        return go(
            token.text,
            token.pos_,
            token.dep_,
            list(token.morph.to_json()),
            i or token.i,
            token.children,
            token.ancestors,
            token.head,
        )

    # @classmethod
    # def from_difftoken(go, token):
    #     if token.lexeme.spacy is None:
    #         return None

    #     return go(
    #         token.lexeme.spacy.text,
    #         token.lexeme.spacy.pos_,
    #         token.lexeme.spacy.dep_,
    #         list(token.lexeme.spacy.morph.to_json()),
    #         token.lexeme.spacy.i,
    #         token.lexeme.spacy.children,
    #         token.lexeme.spacy.ancestors,
    #         token.lexeme.spacy.head,
    #     )

    def __getitem__(self, key) -> str:
        return self.morphs.get(key)

    def __setitem__(self, key, value):
        self.morphs[key] = value


class Fix:
    def __init__(self, correct: GrammarObject, i: int, explanation: str):
        """
        A fix for an incorrect GrammarObject.

        Params:
            - correct: The correct GrammarObject.
            - i: Index of the incorrect object in correction tree.
            - explanation: Explanation of the fix.

        Returns:
            - fix: The Fix object lol.
        """
        self.correct = correct
        self.i = i
        self.explanation = explanation


# Consistency helper functions.


def is_singular(go: GrammarObject) -> bool:
    """
    Figures out whether a GrammarObject is singular.

    Params:
        - go: A GrammarObject.

    Returns:
        - singular: Whether the object is singular.
    """

    if go.pos == "adj":
        if num := go["number"]:
            return num == "sing"
        else:
            return go.text in lemmatizer.lemmatize("ADJ", go.text)
    elif go.pos == "det":
        return "plur" != go["number"]
    else:
        return "sing" == go["number"]


def is_singular_irregular(go: GrammarObject) -> bool:
    """
    Look up irregular verbs for singularity inflections.

    Params:
        - go: GrammarObject to be checked.

    Returns:
        - singular: Whether the object is singular.
    """
    return True  # TODO: Use dictionary.


def is_inconsistent(a: GrammarObject, b: GrammarObject) -> bool:
    """
    Checks numerical consistency between two GrammarObjects.

    Params:
        - a: The primary GrammarObject.
        - b: The secondary GrammarObject.

    Returns:
        - inconsistent: Whether they are inconsistent.
    """

    if b["number"] is None:
        return is_singular_irregular(b) != is_singular(a)
    else:
        return is_singular(b) != is_singular(a)


# Correction dispatch and functions


def fix_pair(a: GrammarObject, b: GrammarObject) -> Fix:
    if (a.pos != "aux" and a.text not in INF_AUX) and b.has("verbform", "inf"):
        if fix := fix_aux_inf(a, b):
            return fix
    else:
        lower_a = a.text.lower()

        if (
            (lower_a in INF_AUX)
            and not b.has("verbform", None)
            and (b.has("verbform", "inf") or b.has("verbform", "fin"))
        ):
            correct = inflect.inflect_verb(b)

            old = b["verbform"]

            b.text = correct
            b["verbform"] = "inf"

            # TODO: Express tense in human language.
            return Fix(b, b.i, f"Forveksling af {old} og infinitiv.")

        # if (lower_a in PAST_AUX) and (b["verbform"] and not b.has("verbform", "part")):
        #     correct = inflect.inflect_verb(b, didize=True)

        #     import pdb

        #     pdb.set_trace()

        #     old = b["verbform"]

        #     # import pdb
        #     # pdb.set_trace()

        #     b.text = correct
        #     b["verbform"] = "part"

        #     # TODO: Express tense in human language.
        #     return Fix(b, b.i, f"Forveksling af {old} og datid")
        # el

        # TODO: Gotta properly handle general cases.
        if False and (
            b.has("verbform", "part")
            and lower_a not in PAST_AUX
            and not b.dep == "ccomp"
        ):
            # The default case is that not clausal component verbs, as well as verbs not bound to a past-aux,
            # ... need to be finite. :)
            correct = inflect.inflect_verb(b, presentize=True)

            old = b["verbform"]

            b.text = correct
            b["verbform"] = "fin"

            # TODO: Express tense in human language.
            return Fix(b, b.i, f"Forveksling af {old} og nutid.")

    if a.pos == "det":

        if a.text.lower() in ["en", "et"]:
            if a["gender"] != b["gender"]:
                correct = a.text.lower() == "et" and "en" or "et"
                gender = correct == "en" and "fælleskøn" or "intetkøn"

                a.text = correct
                a["gender"] = b["gender"]

                return Fix(
                    a,
                    a.i,
                    f'Substantiver af {gender} skal have artiklen "{correct}".',
                )

        elif a.text.lower() in ["sin", "sit"]:
            if a["gender"] != b["gender"]:
                correct = a.text.lower() == "sit" and "sin" or "sit"
                gender = correct == "sin" and "fælleskøn" or "intetkøn"

                a.text = correct
                a["gender"] = b["gender"]

                return Fix(
                    a,
                    a.i,
                    f'Substantiver af {gender} skal have artiklen "{correct}".',
                )

        elif a.text.lower() in ["hendes", "hans", "dens"]:
            if a.head.dep_.lower() == 'nsubj':
                correct = 'sin'

                origin = a.text
                a.text = correct

                return Fix(
                    a,
                    a.i,
                    f'"{origin}" bør ændres til "{a.text}", når ordet binder sig til grundleddet.'
                )

    if a.pos in ["pron", "noun", "det"] and is_inconsistent(a, b):
        correct = b.text
        a_singular = is_singular(a)

        abort_mission = a.text in REFLECTIVE_ADJ

        if not abort_mission:
            # import pdb

            # pdb.set_trace()

            explanation = (
                a_singular
                and f'"{b.text}" skal bøjes i ental her.'
                or f'"{b.text}" skal bøjes i flertal her.'
            )

            if b.pos in ["propn", "noun"]:
                correct = inflect.inflect_noun(
                    b, singularize=a_singular, pluralize=(not a_singular)
                )

            elif b.pos == "adj":
                itk = a.has("gender", "neut")

                if b.has("definite", "def"):
                    abort_mission = True
                else:
                    correct = inflect.inflect_adj(
                        b, itk=itk, pluralize=not a_singular, singularize=a_singular
                    )

                    if itk:
                        explanation = f'"{a.text}" skal bøjes i intetkøn her.'

            if not abort_mission and (b.text != correct):
                b.text = correct
                b["number"] = a["number"]
                b["gender"] = a["gender"]

                return Fix(b, b.i, explanation)

    if a.pos == "adj" and is_inconsistent(a, b):
        b_singular = is_singular(b)
        itk = a.has("gender", "neut") and not b.has("gender", "neut")

        correct = inflect.inflect_adj(
            a, itk=itk, singularize=b_singular, pluralize=not b_singular
        )

        if itk:
            explanation = f'"{a.text}" skal bøjes i intetkøn her.'
        else:
            explanation = (
                b_singular
                and f'"{a.text}" skal bøjes i ental her.'
                or f'"{a.text}" skal bøjes i flertal her.'
            )

        abort_mission = False

        for obj in b.children:
            go_obj = GrammarObject.from_token(obj)
            if (go_obj.dep == "det" and b_singular) and go_obj.has("number", "plur"):
                abort_mission = True
                break

        if not abort_mission and a.text != correct:
            a.text = correct

            a["number"] = b["number"]
            a["gender"] = b["gender"]

            return Fix(a, a.i, explanation)

    if (a.pos == "verb" and a.has("verbform", "inf")) and b.dep == "nsubj":
        # This is a default correction that will be fixed by auxes.

        correct = inflect.inflect_verb(a, presentize=True)

        a.text = correct
        a["verbform"] = "fin"

        return Fix(a, a.i, "Forveksling af infinitiv og nutid")

    if a.dep == "expl" and a.pos in ["noun", "propn"] and b.has("verbform", "part"):
        correct = inflect.inflect_verb(b, presentize=True)

        b.text = correct
        b["verbform"] = "fin"

        return Fix(b, b.i, "Forveksling af datid og nutid.")

    if a.text.lower() in ["ligger", "lægger"]:
        if b.dep == "obj":
            if a.text.lower() == "ligger":
                a.text = "lægger"
                return Fix(a, a.i, "Forveksling af ligger og lægger.")

        elif a.text.lower() == "lægger":
            a.text = "ligger"
            return Fix(a, a.i, "Forveksling af ligger og lægger.")

    return None


def fix_aux_inf(a: GrammarObject, b: GrammarObject) -> Fix:
    """
    Check if the auxiliary verb is bound to an inf verb.

    Example:
        - [wrong] Jeg løbe udenfor.
        - [nice]  Jeg løber udenfor.
    """

    abort_mission = False

    for obj in b.children:
        if obj.dep_ == "aux":
            # There is a modifier for the inf verb.
            # In this case there should be no correction.
            abort_mission = True
            break

    if not abort_mission and a.pos == "cconj":
        for cousin in list(set([a.head] + list(a.ancestors))):
            for obj in cousin.children:
                if obj.dep_ == "aux":
                    abort_mission = True
                    break

        # Construct a dict of possibly conjuncted auxed/marked verb
        # ... Will use this to mirror possibly missing consistency.
        # ... TODO: This fix is used to deal with spaCy dep-fuck.

        cs = dict([(t.text, t.dep_) for t in a.head.head.children])

        if cs[b.text] == "conj" and "mark" in cs.values():
            abort_mission = True

    if abort_mission:
        return None
    else:
        # TODO: Maybe pastize. Keep state of sentence somewhere.
        correct = inflect.inflect_verb(b, presentize=True)

        b.text = correct
        b["verbform"] = "fin"

        return Fix(b, b.i, "Forveksling af infinitiv og nutid.")


def at_og_fixer(unmasker, first_doc, text, changes) -> str:
    """
    Uses BERT to figure out whether something is 'at' or 'og'.
    The function won't do anything if these words do not appear.

    Params:
        - The unmasking language model.
        - first_doc: The initial doc that needs checking.
        - changes: The running change log.

    Returns:
        - text: The corrected text.
        - changes: The updated changes.
    """
    mask_stack = []
    backup_stack = []
    tokens_masked = []

    last_inf = False
    mask_is = []

    count = sum([bool(t.text in ["at", "og"]) for t in first_doc])

    for i_round in range(0, count):
        passed = 0
        tokens_masked = []

        for i, token in enumerate(first_doc):
            if token.pos_ == "VERB" and "inf" in token.morph.verb_form_:
                last_inf = True
                tokens_masked.append(token.text)
            else:
                if token.text.lower() == "og" and last_inf:
                    if passed == i_round:
                        tokens_masked.append("[MASK]")
                        mask_is.append(i)
                        backup_stack.append(token.text)
                    else:
                        tokens_masked.append(token.text)
                    passed += 1
                else:
                    tokens_masked.append(token.text)

                last_inf = False

        mask_stack.append(tokens_masked)

    if len(mask_stack) > 0:
        final_mask = mask_stack[0].copy()

        if len(mask_is) > 0:
            final_mask[mask_is[0]] = backup_stack[0]

        for i, mask_i in enumerate(mask_is):
            tokens_masked, backup = mask_stack[i], backup_stack[i]
            text_masked = " ".join(tokens_masked).replace(" ,", ",").replace(" .", ".")

            tokens = list(
                filter(
                    lambda t: t in ["at", "og"],
                    [x["token_str"] for x in unmasker(text_masked)],
                )
            )

            if len(tokens) > 0:
                correct = tokens[0]

                if correct != backup:
                    explain.append_change(
                        changes,
                        mask_i,
                        explain.change("change", correct, f'Forkert brug af "og".'),
                    )

                final_mask[mask_i] = correct
            else:
                final_mask[mask_i] = backup

        text = " ".join(final_mask).replace(" ,", ",").replace(" .", ".")

    return text, changes


def af_ad_fixer(unmasker, first_doc, text, changes) -> str:
    """
    Uses BERT to figure out whether something is 'ad' or 'af'.
    The function won't do anything if these words do not appear.

    Params:
        - The unmasking language model.
        - first_doc: The initial doc that needs checking.
        - changes: The running change log.

    Returns:
        - text: The corrected text.
        - changes: The updated changes.
    """
    mask_stack = []
    backup_stack = []
    mask_is = []

    last_inf = False

    count = sum([bool(t.text in ["af", "ad"]) for t in first_doc])

    for i_round in range(0, count):
        passed = 0
        tokens_masked = []

        for i, token in enumerate(first_doc):
            if token.text.lower() in ["af", "ad"]:
                if passed == i_round:
                    tokens_masked.append("[MASK]")
                    mask_is.append(i)
                    backup_stack.append(token.text)
                else:
                    tokens_masked.append(token.text)
                passed += 1
            else:
                tokens_masked.append(token.text)

        mask_stack.append(tokens_masked)

    if len(mask_stack) > 0:
        # Construct clean version: speed trick *drift*
        final_mask = mask_stack[0].copy()
        final_mask[mask_is[0]] = backup_stack[0]

        for i, mask_i in enumerate(mask_is):
            tokens_masked, backup = mask_stack[i], backup_stack[i]
            text_masked = " ".join(tokens_masked).replace(" ,", ",").replace(" .", ".")

            tokens = list(
                filter(
                    lambda t: t in ["ad", "af"],
                    [x["token_str"] for x in unmasker(text_masked) if x["score"] > 0.9],
                )
            )

            if len(tokens) > 0:
                correct = tokens[0]

                if correct != backup:
                    explain.append_change(
                        changes,
                        mask_i,
                        explain.change(
                            "replace", correct, f'Det korrekte ord er "{correct}".'
                        ),
                    )

                final_mask[mask_i] = correct
            else:
                final_mask[mask_i] = backup

        text = " ".join(final_mask).replace(" ,", ",").replace(" .", ".")

    return text, changes


# Correction helper functions.


def capitalize_name(go, changes, i, split_i):
    if go.text[0].lower() == go.text[0]:
        correct = go.text.capitalize() + " "

        explanation = ["Dette egenavn bør have stort begyndelsesbogstav."]
        explain.insert_change(
            changes,
            i,
            split_i,
            explain.change("replace", correct, explanation),
            explanation,
        )

        return correct

    return go.text


def fix_lays(token, changes, change_map, fix_map):
    change = change_map[token.i]
    map_i = change[1]
    split_i = change[2]

    explain.insert_append_change(
        changes,
        map_i,
        split_i,
        explain.change("change", "ligger", "Forveksling af lægger og ligger."),
        "Forveksling af lægger og ligger.",
    )

    fix_map[token.i] = "ligger"


# Grammar tree growing functions.


def siblings(token):
    result = token.head == token and [] or [token.head]

    for child in token.head.children:
        if child == token:
            continue

        result.append(child)

    return list(set(result))


def nsubj_pair(token):
    return [token.head]


def root_pair(token):
    if token.text in ["ligger", "lægger"]:
        return [t for t in token.children if t.dep_ == "obj"]
    else:
        return []


def det_pair(token):
    if token.head.pos_ == "NOUN":
        return [token.head]
    else:
        return [t for t in siblings(token) if t.pos_ in ["ADJ", "NOUN"]][:1]


def amod_pair(token):
    if token.head.dep_ in ["nsubj", "ROOT"]:
        return [token.head]
    else:
        return [t for t in token.children if t.dep_ == "nsubj"]


def aux_pair(token):
    return [token.head]


def xcomp_pair(token):
    return [t for t in siblings(token) if t.dep_ == "nsubj"]


def expl_pair(token):
    return [t for t in siblings(token) if t.pos_ == "VERB"]


def cc_pair(token):
    return list(set([token.head]))  # + list(token.ancestors)))


def mark_pair(token):
    if token.text.lower() == "at":
        return [token.head]
    else:
        return []


def grammar_tree(token):
    """
    Maps tokens with their grammatical pairs.

    Params:
        - token: spaCy Token to be mapped from.
        - doc: The spaCy Doc to map over.

    Returns:
        - pair: The pair with the token.
    """

    if func := {
        "nsubj": nsubj_pair,
        "root": root_pair,
        "det": det_pair,
        "amod": amod_pair,
        "aux": aux_pair,
        "xcomp": xcomp_pair,
        "expl": expl_pair,
        "cc": cc_pair,
        "mark": mark_pair,
    }.get(token.dep_.lower()):
        return func(token)
    else:
        return None


def init(unmasker, nlp):
    def fix(diff: List[DiffToken] = [], text=""):

        upper_mask = [t[0].isupper() and not i == 0 for i, t in enumerate(util.parse_words(text, nlp=nlp, lower=False))]
        first_doc = nlp(text)

        # spacy.displacy.serve(first_doc, style='dep')

        changes = list(
            map(lambda t: {"origin": t.text + t.whitespace_, "type": "none"}, first_doc)
        )

        text, changes = at_og_fixer(unmasker, first_doc, text, changes)
        text, changes = af_ad_fixer(unmasker, first_doc, text, changes)

        # doc = nlp(text)
        doc = nlp(text)
        change_map = explain.change_map(changes)

        # TODO: Things and stuff.
        # NOTE:
        # - A map of all corrections need to be maintained.
        # - Every relative's index in this map is looked up and shadows.
        #   * This will almost definitely need exceptions of sorts.
        # - Inflections need GrammarObjects.
        # - Fix shall convert to change.
        # - Fixer function shall construct Fixes properly.
        #   * This is done by overlapping GrammarObjects.

        # result = []
        result_fix_map = dict()
        correction_lookup = dict()

        for (_, i, split_i), token in zip(change_map, doc):
            # print('----')
            # pprint(token)

            if i < len(upper_mask) and upper_mask[i]:
                continue

            new_tokens = tokenize(str(token.text))
            non_punct = list(
                filter(
                    lambda t: t.lexeme.type in (LexemeType.WORD, LexemeType.NUMB),
                    new_tokens,
                )
            )
            if len(non_punct) == 0:
                continue

            go = GrammarObject.from_token(token)
            # print(f'- {go.text}: {go.pos} @ {go.dep} @ {list(go.ancestors)}')

            # pprint(go)
            # result.append(token.text)

            # print()
            # print(
            #     f"{token.text}({token.pos_}) @ {token.dep_} & {token.morph.to_json()}"
            # )

            if relatives := grammar_tree(token):

                for cousin in relatives:

                    go_cousin = correction_lookup.get(
                        cousin.i
                    ) or GrammarObject.from_token(cousin)
                    # pprint(go_cousin)
                    # print(f"- {go_cousin.text} {go_cousin.dep} {go_cousin.pos}")

                    if fix := fix_pair(go, go_cousin):
                        if fix.correct.text == changes[fix.i]["origin"].strip():
                            changes[fix.i] = {
                                "type": "none",
                                "origin": changes[fix.i]["origin"],
                            }
                            continue

                        change = change_map[fix.i]
                        map_i = change[1]
                        map_split_i = change[2]

                        explain.insert_append_change(
                            changes,
                            map_i,
                            map_split_i,
                            explain.change(
                                "replace", fix.correct.text, fix.explanation
                            ),
                            fix.explanation,
                        )

                        # print(f"--> {fix.i} {fix.correct.text}: {fix.explanation}")

                        result_fix_map[fix.i] = fix.correct.text
                        correction_lookup[fix.i] = fix.correct
            else:
                if token.text in ["lægger", "ligger"]:
                    fix_lays(token, changes, change_map, result_fix_map)

            # TODO: Fucking NER
            if go.pos == 'propn':
                if name := NAMES.get(go.text.lower(), False):
                    result_fix_map[go.i] = capitalize_name(name, changes, i, split_i)

        # print()
        # draw_tree(doc)
        # print()

        # for i, word in result_fix_map.items():
        #     result[i] = word

        corrected = list(map(DiffToken.from_dict, changes))

        changes = []
        for c in corrected:
            if c.lexeme.type == LexemeType.SPAC:
                if len(changes) == 0:
                    changes.append(c)
                else:
                    changes[-1].lexeme.space += c.lexeme.space
            else:
                changes.append(c)

        changes = DiffToken.flatten(changes)

        for i, change in enumerate(changes):
            # prevent non-word spelling changes from leaking through
            # if a non-word is converted into a word by spelling,
            #   it will break the pipeline down the road due to removed words and different tokenization
            if change.lexeme.type != LexemeType.WORD:
                changes[i] = diff[i].clone_clean()
            else:
                # copy down space because grammar eats it
                change.lexeme.space = diff[i].lexeme.space
            changes[i].index = i

        return changes, "".join(map(str, changes))

    return fix


if __name__ == "__main__":
    from transformers import pipeline, AutoTokenizer, AutoModelForPreTraining

    tokenizer = AutoTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
    unmasker = pipeline(
        "fill-mask", model="Maltehb/danish-bert-botxo", tokenizer=tokenizer
    )
    nlp = spacy.load("da_core_news_lg")

    fix = init(unmasker, nlp)

    while True:
        text = input("> ")

        changes = [explain.change("none", t) for t in text.split(" ")]

        print(fix(text, changes))
