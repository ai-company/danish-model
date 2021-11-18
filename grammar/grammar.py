from pprint import pprint
from typing import List
from diff_token import DiffToken, LexemeType, tokenize
from dataclasses import dataclass

from spacy.symbals import nsubj, VERB, ADJ
from spacy.matcher import DependencyMatcher

from nltk import Tree
from textacy.spacier import utils as spacy_utils

from ..spell import explain, util

import spacy
import lemmy
import os


lemmatizer = lemmy.load('da')


class Sentence:
    def __init__(self, text, nlp, matcher):
        self.text = text
        self.doc  = nlp(text)

    def svo_triples(self):
        for sent in self.doc.sents:
            start_i = sent[0].i

            verbs = spacy_utils.get_main_verbs_of_sentence(sent)
            for verb in verbs:
                subjects = spacy_utils.get_subject_of_verb(verb)

                if not subjects:
                    continue

                objects = spacy_utils.get_objects_of_verb(verb)

                if not objects:
                    continue

                verb_span = spacy_utils.get_span_for_verb_auxiliaries(verb)
                verb = sent[verb_span[0] - start_i : verb_span[1] - start_i + 1]

                for subject in subjects:
                    subject = sent[
                        spacy_utils.get_span_for_compound_noun(subject)[0]
                            - start_i : subject.i - start_i + 1]

                    for object in objects:
                        if object.pos_ == 'NOUN':
                            span = spacy_utils.get_span_for_compound_noun(object)
                        elif object.pos_ == 'VERB':
                            span = spacy_utils.get_span_for_verb_auxiliaries(object)
                        else:
                            span = (object.i, object.i)

                        object = sent[span[0] - start_i : span[1] - start_i + 1]

                        yield (subject, verb, object)

    def chunks(self):
        chunks = []

        for chunk in self.doc.noun_chunks:
            meta = dict()
            meta[chunk.root.pos_] = chunk.root

            for token in chunk:
                if token != chunk.root:
                    meta[token.pos_] = token

            chunks.append(meta)

        return chunks

    def debug(self):
        [branch.pretty_print() for branch in Sentence.to_tree(self.doc)]

    @staticmethod
    def to_tree(doc):
        tree = []
        for sent in doc.sents:
            node = sent.root
            branch = node.orth_

            if node.n_lefts + node.n_rights > 0:
                branch = Tree(node.orth_, [Sentence.to_tree(node.children)])

            tree.append(branch)

        return tree
