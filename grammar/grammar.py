from pprint import pprint
from typing import List, Dict, Union
# from diff_token import DiffToken, LexemeType, tokenize
from dataclasses import dataclass

from spacy.symbols import nsubj, VERB, ADJ
from spacy.matcher import DependencyMatcher

from nltk import Tree
from textacy.spacier import utils as spacy_utils

# from ..spell import explain, util

import spacy
import lemmy
import os


lemmatizer = lemmy.load('da')

GENDER_DETS = {
    'Com':  'en',
    'Neut': 'et'
}

# Gangster Token
class GToken:
    __slots__ = ('token', 'text')

    def __init__(self, token):
        self.token = token
        self.text = token.text

    def __repr__(self):
        return '<"' + self.text + '">'

class Fix:
    def __init__(self, correct: GToken, i: int, explanation: str):
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
        self.trace = None

        if os.getenv('TRACE_EXPLANATIONS', '') == 'TRUE':
            from inspect import getframeinfo, stack

            caller = getframeinfo(stack()[1][0])
            self.trace = f'{caller.filename}:{caller.lineno}'



@dataclass
class ChunkInfo:
    __slots__ = ('token', 'morph')

    token: any
    morph: Dict[str, str]


class Sentence:
    def __init__(self, text, nlp):
        self.text = text
        self.doc  = nlp(text)

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
                            - start_i : subject.i - start_i + 1]

                    if not objects:
                        yield (subject, verb, None)

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
            meta[chunk.root.pos_] = ChunkInfo(GToken(chunk.root), chunk.root.morph.to_dict())

            for token in chunk:
                if token != chunk.root:
                    meta[token.pos_] = ChunkInfo(GToken(token), token.morph.to_dict())

            chunks.append(meta)

        return chunks

    def debug(self):
        delim = '=' * (len(self.text) + 2)

        print(delim)
        print(f'"{self.text}"\n')
        print('noun chunks:')
        pprint(self.chunks())

        print()
        self.print_tree()

        print()
        print('triples (subject | verb | object):')

        for s, v, o in self.svo_triples():
            print(f'- {s} | {v} | {o}')

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
            return Tree(node.orth_, [Sentence.nltk_tree(child) for child in node.children])
        else:
            return node.orth_

def modify(original, text, morph):
    return original, ChunkInfo(GToken(original.token, text), morph)

def fix_chunk_genders(chunk: Dict[str, ChunkInfo]) -> Union[Fix, None]:
    if 'NOUN' in chunk and 'DET' in chunk:
        target_gender = chunk['NOUN'].morph['Gender']

        original, new = modify(
            chunk,
            GENDER_DETS[target_gender],
            target_gender
        )

        chunk['DET'].token.text = GENDER_DETS[target_gender]
        chunk['DET'].morph['Gender'] = target_gender

        return Fix()


nlp = spacy.load('da_core_news_lg')
s = Sentence('niels spise et kæmpe kylling.', nlp)

s.debug()

print('fix:')
for chunk in s.chunks():
    fix_chunk_genders(chunk)
    print('-', chunk)
