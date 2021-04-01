# coding: utf-8

from __future__ import division
import sys
from os.path import join, dirname
import collections
import json

import tensorflow as tf
import numpy as np
import spacy
from pysbd.utils import PySBDFactory

from . import convert, explain, model, data, clauses
from .config import MINIBATCH_SIZE


def make_tag(t):
    result = ''

    t = t.split('__')

    result += t[0][:2]

    t = str(t[1:]).split('|')

    hash = {}

    for n in t:
        if '=' in n:
            ass = n.split('=')
            hash[ass[0]] = ass[1]

    hash = collections.OrderedDict(sorted(hash.items()))
    result += ''.join([v[0] for _, v in hash.items()])

    return result


def to_array(arr, dtype=np.int32):
    return np.array([arr], dtype=dtype).T


def convert_punctuation_to_readable(punct_token):
    if punct_token == data.SPACE:
        return " "
    else:
        return punct_token[0]


def punctuate(word_vocabulary, punctuation_vocabulary, reverse_punctuation_vocabulary, text, model):
    if len(text) == 0:
        return ''

    text = [w for w in text.split() if w not in punctuation_vocabulary] + \
        [data.END]
    i = 0

    result = ''

    while True:
        subsequence = text[i:i+data.MAX_SEQUENCE_LEN]

        if len(subsequence) == 0:
            break

        converted_subsequence = [word_vocabulary.get(
            w, word_vocabulary[data.UNK]) for w in subsequence]

        y = predict(to_array(converted_subsequence), model)

        last_eos_idx = 0
        punctuations = []
        for y_t in y:
            p_i = np.argmax(tf.reshape(y_t, [-1]))

            punctuation = reverse_punctuation_vocabulary[min(
                p_i, len(reverse_punctuation_vocabulary) - 1)]

            punctuations.append(punctuation)

            if punctuation in data.EOS_TOKENS:
                last_eos_idx = len(punctuations)

        if subsequence[-1] == data.END:
            step = len(subsequence) - 1
        elif last_eos_idx != 0:
            step = last_eos_idx
        else:
            step = len(subsequence) - 1

        token = ''

        for j in range(step):
            if j > 0:
                token += ' '

            token = punctuations[j] + \
                " " if punctuations[j] != data.SPACE else " "
            result += token

            if j < step - 1:
                result += subsequence[1+j]

        if subsequence[-1] == data.END:
            break

        i += step

    return result


def predict(x, model):
    return tf.nn.softmax(model(x))


def init():
    """
    Comma correction factory; loading models and returning closure for commarization.

    Returns:
        - process: Closure for processing/commarization. 
    """
    nlp = spacy.load('da_core_news_lg')

    model_file = join(dirname(__file__), 'data/model.pcl')

    vocab_len = len(data.read_vocabulary(data.WORD_VOCAB_FILE))
    x_len = vocab_len if vocab_len < data.MAX_WORD_VOCABULARY_SIZE else data.MAX_WORD_VOCABULARY_SIZE + \
        data.MIN_WORD_COUNT_IN_VOCAB
    x = np.ones((x_len, MINIBATCH_SIZE)).astype(int)

    net, _ = model.load(model_file, x)

    word_vocabulary = net.x_vocabulary
    punctuation_vocabulary = net.y_vocabulary
    reverse_punctuation_vocabulary = {
        v: k for k, v in net.y_vocabulary.items()}

    def commarize_sentence(text):
        if len(text.strip()) == 0:
            return ''

        encoded_text = ' '.join([make_tag(t.tag_) for t in nlp(text)]).lower()

        result = punctuate(word_vocabulary, punctuation_vocabulary,
                           reverse_punctuation_vocabulary, encoded_text, net)
        result = result.replace('?QUESTIONMARK', '')

        result = f'{encoded_text.split(" ")[0]}{result}'
        result = convert.convert(result, text)
        result = f'{result[0].upper()}{result[1:]}'

        return result

    def process(text, changes):
        """
        Text processing closure for commarizing and explaining fixes.

        Params:
            - text: Text to be processed.
            - changes: A reference to incremental changelog.

        Returns:
            - result: The processed text.
            - changes: Updated list of explanations for changes made to the input text.
        """

        result = clauses.heuristics(nlp(commarize_sentence(text)))

        # Add last comma.
        if c := result[-1:] not in '.?!':
            if c == ',':
                result = result[:-1] + '.'
            else:
                result += '.'

        explanations = explain.get_explanations(result)

        tokens = result.split()

        change_map = explain.change_map(changes)

        comma_i = 1

        for (change, i, split_i), token in zip(change_map, tokens):
            if token.lower().replace(',', '').replace('.', '') == change \
                    and token.replace(',', '').replace('.', '') != change:

                i = i + comma_i - 1

                explanation = 'Stort begyndelsesbogstav.'

                if changes[i]['type'] == 'none':
                    changes[i]['type'] = 'replace'
                    changes[i]['change'] = token
                    changes[i]['explain'] = explanation
                else:
                    capital_change = explain.change(
                        'replace', token, explanation)

                    explain.insert_change(
                        changes, i, split_i, capital_change, explanation)

            if ',' in token:
                explanation = 'Der bør være et komma her.'

                if comma_i < len(explanations):
                    explanation = explanations[comma_i]

                changes.insert(
                    i + comma_i,
                    explain.explain(
                        'add',
                        change=',',
                        explanation=explanation
                    )
                )

                comma_i += 1

            elif '.' in token:
                changes.insert(
                    i + comma_i,
                    explain.explain(
                        'add',
                        change='.',
                        explanation='Sætningen bør afsluttes med et punktum.'
                    )
                )

        return changes, result

    return process
