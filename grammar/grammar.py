#!/usr/bin/env python3

import spacy
import lemmy
import textacy
import explain
import util
import grammar.inflect as inflect
import pandas as pd
import os
import itertools

from pprint import pprint
from spacy.symbols import nsubj, VERB, ADJ
from spacy.matcher import DependencyMatcher

from nltk import Tree
from textacy.spacier import utils as spacy_utils
from diff_token import DiffToken, LexemeType, tokenize
from transformers import pipeline, AutoTokenizer, AutoModelForPreTraining
from typing import List
from dataclasses import dataclass

lemmatizer = lemmy.load("da")

NAMES = dict(
    zip(
        pd.read_excel(os.path.join(os.path.dirname(__file__), "data/names.xlsx"))["Ab"]
        .apply(lambda x: x.lower())
        .tolist(),
        itertools.cycle([True]),
    )
)
SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]


class GrammarObject:
    def __init__(
        self,
        text: str,
        pos: str,
        dep: str,
        morphs: List[str],
        i: int,
        children: List[any],
        ancestors: List[any],
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

    def __getitem__(self, key) -> str:
        return self.morphs.get(key)

    def __setitem__(self, key, value):
        self.morphs[key] = value


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


@dataclass
class Fix:
    """
    A fix for an incorrect GrammarObject.

    Params:
        - correct: The correct GrammarObject.
        - i: Index of the incorrect object in correction tree.
        - explanation: Explanation of the fix.

    Returns:
        - fix: The Fix object lol.
    """

    correct: GrammarObject
    i: int
    explanation: str


class Sentence:
    def __init__(self, text, nlp):
        self.text = text
        self.doc = nlp(text)

    def sv_pairs(self):
        sv_list = []

        for sent in self.doc.sents:
            verbs = spacy_utils.get_main_verbs_of_sent(sent)

            for verb in verbs:
                subjects, negated = Sentence.get_subjects(verb)

                if len(subjects) > 0:
                    for subject in subjects:
                        sv_list.append((subject, verb))  # TODO: negated mby

        return sv_list

    def svo_triples(self):
        for sent in self.doc.sents:
            start_i = sent[0].i

            verbs = spacy_utils.get_main_verbs_of_sent(sent)

            for verb in verbs:
                subjects = spacy_utils.get_subjects_of_verb(verb)

                objects = spacy_utils.get_objects_of_verb(verb)

                verb_span = spacy_utils.get_span_for_verb_auxiliaries(verb)
                verb = sent[verb_span[0] - start_i : verb_span[1] - start_i + 1]

                for subject in subjects:
                    subject = sent[
                        spacy_utils.get_span_for_compound_noun(subject)[0]
                        - start_i : subject.i
                        - start_i
                        + 1
                    ]

                    if not objects:
                        yield (subject[0], verb[0], None)

                    for object in objects:
                        if object.pos_ == "NOUN":
                            span = spacy_utils.get_span_for_compound_noun(object)
                        elif object.pos_ == "VERB":
                            span = spacy_utils.get_span_for_verb_auxiliaries(object)
                        else:
                            span = (object.i, object.i)

                        object = sent[span[0] - start_i : span[1] - start_i + 1]

                        yield (subject[0], verb[0], object)

    def chunks(self):
        chunks = []

        for chunk in self.doc.noun_chunks:
            meta = dict()
            meta[chunk.root.pos_] = ChunkInfo(
                GToken(chunk.root), chunk.root.morph.to_dict()
            )

            for token in chunk:
                if token != chunk.root:
                    meta[token.pos_] = ChunkInfo(GToken(token), token.morph.to_dict())

            chunks.append(meta)

        return chunks

    def debug(self):
        delim = "=" * (len(self.text) + 2)

        print(delim)
        print(f'"{self.text}"\n')
        print("noun chunks:")
        pprint(self.chunks())

        print()
        self.print_tree()

        print()
        print("triples (subject | verb | object):")

        for s, v, o in self.svo_triples():
            print(f"- {s} | {v} | {o}")

        print(delim)

    def print_tree(self):
        for sent in self.doc.sents:
            if c := Sentence.nltk_tree(sent.root):
                if type(c) == str:
                    print(c)
                else:
                    c.pretty_print()

    @staticmethod
    def nltk_tree(node):
        if node.n_lefts + node.n_rights > 0:
            return Tree(
                node.orth_, [Sentence.nltk_tree(child) for child in node.children]
            )
        else:
            return node.orth_

    @staticmethod
    def get_subjects_of_conjunctions(subjects):
        more = []

        for sub in subjects:
            rights = list(sub.rights)
            right_deps = [t.lower_ for t in rights]

            if "og" in right_deps:
                more.extend(
                    [t for t in rights if t.dep_ in SUBJECTS or t.pos_ == "NOUN"]
                )

                if len(more) > 0:
                    more.extend(Sentence.get_subjects_of_conjunctions(more))

        return more

    @staticmethod
    def get_subjects(token):
        negated = Sentence.is_negated(token)
        subjects = [t for t in token.lefts if t.dep_ in SUBJECTS and t.pos_ != "DET"]

        if len(subjects) > 0:
            subjects.extend(Sentence.get_subjects_of_conjunctions(subjects))
        else:
            found, negated = Sentence.find_subjects(token)
            subjects.extend(found)

        return subjects, negated

    @staticmethod
    def find_subjects(token):
        head = token.head  # Get head.
        while head.pos_ not in ["VERB", "NOUN"] and head.head != head:
            head = head.head

        if head.pos_ == "VERB":
            subjects = [token for token in head.lefts if token.dep_ == "SUB"]

            if len(subjects) > 0:
                negated = Sentence.is_negated(head)
                subjects.extend(Sentence.get_subjects_of_conjunctions(subjects))

                return subjects, negated

            elif head.head != head:
                return Sentence.find_subjects(head)
        elif head.pos_ == "NOUN":
            return [head], Sentence.is_negated(token)

        return [], False

    @staticmethod
    def is_negated(token):
        negations = ["ikke", "ingen", "intet", "aldrig", "ingen"]

        for dep in list(token.lefts) + list(token.rights):
            if dep.lower_ in negations:
                return True
        return False


class SentenceTree:
    @staticmethod
    def siblings(token):
        result = token.head == token and [] or [token.head]

        for child in token.head.children:
            if child == token:
                continue

            result.append(child)

        return list(set(result))

    @staticmethod
    def nsubj_pair(token):
        return [token.head]

    @staticmethod
    def root_pair(token):
        if token.text in ["ligger", "lægger"]:
            return [t for t in token.children if t.dep_ == "obj"]
        else:
            return []

    @staticmethod
    def det_pair(token):
        if token.head.pos_ == "NOUN":
            return [token.head]
        else:
            return [
                t for t in SentenceTree.siblings(token) if t.pos_ in ["ADJ", "NOUN"]
            ][:1]

    @staticmethod
    def amod_pair(token):
        if token.head.dep_ in ["nsubj", "ROOT"]:
            return [token.head]
        else:
            return [t for t in token.children if t.dep_ == "nsubj"]

    @staticmethod
    def aux_pair(token):
        return [token.head]

    @staticmethod
    def xcomp_pair(token):
        return [t for t in SentenceTree.siblings(token) if t.dep_ == "nsubj"]

    @staticmethod
    def expl_pair(token):
        return [t for t in SentenceTree.siblings(token) if t.pos_ == "VERB"]

    @staticmethod
    def cc_pair(token):
        return list(set([token.head]))  # + list(token.ancestors)))

    @staticmethod
    def mark_pair(token):
        if token.text.lower() == "at":
            return [token.head]
        else:
            return []

    @classmethod
    def grammar_tree(tree, token):
        """
        Maps tokens with their grammatical pairs.

        Params:
            - token: spaCy Token to be mapped from.
            - doc: The spaCy Doc to map over.

        Returns:
            - pair: The pair with the token.
        """

        if func := {
            "nsubj": tree.nsubj_pair,
            "root": tree.root_pair,
            "det": tree.det_pair,
            "amod": tree.amod_pair,
            "aux": tree.aux_pair,
            "xcomp": tree.xcomp_pair,
            "expl": tree.expl_pair,
            "cc": tree.cc_pair,
            "mark": tree.mark_pair,
        }.get(token.dep_.lower()):
            return func(token)
        else:
            return []


class Correct:
    @staticmethod
    def fix_nutids_r(text, changes, nlp):
        s = Sentence(text, nlp)

        for (s, v, _) in s.svo_triples():

            # Can't do that, if auxiliary verbs exist.
            if len([t for t in v.children if t.dep_ == "aux"]) > 0:
                continue

            go_s = GrammarObject.from_token(s)
            go_v = GrammarObject.from_token(v)

            # OMG, what a cool hack. You must be ultra-smart.
            # > Yes, thank.
            if go_v.has("verbform", "inf") or go_v.text in inflect.verb_inflections:
                correct = inflect.inflect_verb(go_v, True)

                if correct != go_v.text:
                    explain.append_change(
                        changes,
                        v.i,
                        explain.change(
                            "change", correct, f"Forveksling af infinitiv og nutid."
                        ),
                    )

                    break

        return changes

    @staticmethod
    def fix_pair(a: GrammarObject, b: GrammarObject):
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

        return None

    @staticmethod
    def at_vs_og(unmasker, first_doc, text, changes) -> str:
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
                text_masked = (
                    " ".join(tokens_masked).replace(" ,", ",").replace(" .", ".")
                )

                result = unmasker(text_masked)
                tokens = list(
                    filter(
                        lambda t: t in ["at", "og"],
                        [x["token_str"] for x in result],
                    )
                )

                if len(tokens) > 0 and result[0]["score"] > 0.85:
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

    @staticmethod
    def af_vs_ad(unmasker, first_doc, text, changes) -> str:
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
                text_masked = (
                    " ".join(tokens_masked).replace(" ,", ",").replace(" .", ".")
                )

                tokens = list(
                    filter(
                        lambda t: t in ["ad", "af"],
                        [
                            x["token_str"]
                            for x in unmasker(text_masked)
                            if x["score"] > 0.9
                        ],
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


def funnel_changes(changes, diff):
    corrected = list(map(DiffToken.from_dict, changes))

    changes = []
    for c in corrected:
        if c.lexeme.type == LexemeType.SPAC:
            if len(changes) == 0:
                changes.append(c)
            else:
                changes[-1].lexeme.space += c.lexeme.text
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

    return changes


def init(unmasker, nlp):
    def fix(diff: List[DiffToken] = [], text=""):

        # What's updog?
        upper_mask = [
            t[0].isupper() and not i == 0
            for i, t in enumerate(util.parse_words(text, nlp=nlp, lower=False))
        ]
        doc = nlp(text)

        changes = list(
            map(lambda t: {"origin": t.text + t.whitespace_, "type": "none"}, doc)
        )

        text, changes = Correct.at_vs_og(unmasker, doc, text, changes)
        text, changes = Correct.af_vs_ad(unmasker, doc, text, changes)

        result_fix_map = dict()
        correction_lookup = dict()

        doc = nlp(text)  # It's better now.
        change_map = explain.change_map(changes)

        # Helper for setting fix
        def go_fix(fix):
            change = change_map[fix.i]
            map_i = change[1]
            map_split_i = change[2]

            explain.insert_append_change(
                changes,
                map_i,
                map_split_i,
                explain.change("replace", fix.correct.text, fix.explanation),
                fix.explanation,
            )

            result_fix_map[fix.i] = fix.correct.text
            correction_lookup[fix.i] = fix.correct

        # Correcting things based on weird spaCy pairs:

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
            tree = SentenceTree.grammar_tree(token)

            if go.text.lower() in ["lægger", "ligger", "lægge", "ligge"]:
                found_obj = False
                abort_mission = False

                if len(tree) == 0:  # We're dealing with a head.
                    tree = list(go.children)

                for pair in tree:
                    go_link = correction_lookup.get(pair.i) or GrammarObject.from_token(
                        pair
                    )

                    if go_link.dep == "obj":
                        found_obj = True

                    if go.text.lower() == "lægge":
                        if (
                            go_link.dep == "mark"
                            and go_link.text.lower() == "at"
                            and go_link.head == token
                        ):
                            # If the mark 'at' is used, it's okay.
                            abort_mission = True

                if not abort_mission:
                    if found_obj:
                        if "li" in go.text.lower():
                            before = go.text
                            go.text = go.text.replace("i", "æ")
                            go_fix(
                                Fix(
                                    go,
                                    go.i,
                                    f'Forveksling af "{before}" og "{go.text}".',
                                )
                            )
                    elif "læ" in go.text.lower():
                        before = go.text
                        go.text = go.text.replace("æ", "i")
                        go_fix(
                            Fix(go, go.i, f'Forveksling af "{before}" og "{go.text}".')
                        )
            else:
                for pair in tree:
                    go_link = correction_lookup.get(pair.i) or GrammarObject.from_token(
                        pair
                    )

                    if fix := Correct.fix_pair(go, go_link):
                        if fix.correct.text == changes[fix.i]["origin"].strip():
                            changes[fix.i] = {
                                "type": "none",
                                "origin": changes[fix.i]["origin"],
                            }
                        else:
                            go_fix(fix)

                if go.pos == "propn":
                    if NAMES.get(go.text.lower(), False):
                        if go.text[0].islower():
                            go.text = go.text.capitalize()
                            go_fix(
                                Fix(
                                    go,
                                    go.i,
                                    "Dette egenavn bør have stort begyndelsesbogstav.",
                                )
                            )

        # Make changes ready for next step:
        # > Your're welcom comas.
        changes = funnel_changes(changes, diff)

        return changes, "".join(map(str, changes))

    def fix_more(diff, text):
        changes = list(map(lambda x: x.to_dict(), diff))

        # And last, but not least ... motherfucking nutids-r.
        changes = Correct.fix_nutids_r(text, changes, nlp)

        changes = funnel_changes(changes, diff)
        text = "".join(map(str, changes))

        return changes, text

    return fix, fix_more
