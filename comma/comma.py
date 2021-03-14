# coding: utf-8

from __future__ import division

import model, data, train

import sys
import tensorflow as tf
import numpy as np

import spacy
import collections
import convert

import explain
import json

from pysbd.utils import PySBDFactory

from os.path import join, dirname

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

    text = [w for w in text.split() if w not in punctuation_vocabulary] + [data.END]
    i    = 0

    result = ''

    while True:
        subsequence = text[i:i+data.MAX_SEQUENCE_LEN]

        if len(subsequence) == 0:
            break

        converted_subsequence = [word_vocabulary.get(w, word_vocabulary[data.UNK]) for w in subsequence]

        y = predict(to_array(converted_subsequence), model)

        last_eos_idx = 0
        punctuations = []
        for y_t in y:
            p_i = np.argmax(tf.reshape(y_t, [-1]))

            punctuation = reverse_punctuation_vocabulary[min(p_i, len(reverse_punctuation_vocabulary) - 1)]

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

            token = punctuations[j] + " " if punctuations[j] != data.SPACE else " "
            result += token

            if j < step - 1:
                result += subsequence[1+j]

        if subsequence[-1] == data.END:
            break

        i += step

    return result

def predict(x, model):
    return tf.nn.softmax(net(x))

def hardcode_commas(text):
    # Also add between multiple adjectives in a row
    return text.replace(' men ', ', men ').replace(',,', ',')

if __name__ == "__main__":
    nlp = spacy.load('da_core_news_lg')

    model_file = join(dirname(__file__), 'punctdata/model_dan_128_0.02.pcl')

    vocab_len = len(data.read_vocabulary(data.WORD_VOCAB_FILE))
    x_len = vocab_len if vocab_len < data.MAX_WORD_VOCABULARY_SIZE else data.MAX_WORD_VOCABULARY_SIZE + data.MIN_WORD_COUNT_IN_VOCAB
    x = np.ones((x_len, train.MINIBATCH_SIZE)).astype(int)

    net, _ = model.load(model_file, x)

    word_vocabulary = net.x_vocabulary
    punctuation_vocabulary = net.y_vocabulary
    reverse_punctuation_vocabulary = {v:k for k,v in net.y_vocabulary.items()}

    print(reverse_punctuation_vocabulary)

    def commarize_sentence(text):
        if len(text.strip()) == 0:
            return ''

        encoded_text = ' '.join([make_tag(t.tag_) for t in nlp(text)]).lower()

        result = punctuate(word_vocabulary, punctuation_vocabulary, reverse_punctuation_vocabulary, encoded_text, net)
        result = result.replace('?QUESTIONMARK', '')

        result = f'{encoded_text.split(" ")[0]}{result}'
        result = convert.convert(result, text)
        result = f'{result[0].upper()}{result[1:]}'

        return result

    sent_nlp = spacy.load('da_core_news_lg')
    sent_nlp.add_pipe(PySBDFactory(sent_nlp), first=True)

    print('<ready>')

    while True:
        text = input("").replace('\0', '\n').replace(',', '')
        doc = sent_nlp(text)

        result = ''.join([commarize_sentence(sent.string) for sent in doc.sents]).replace('\n', '\0')

        if c := result[-1:] not in '.?!':
            if c == ',':
                result = result[:-1] + '.'
            else:
                result += '.'

        result = hardcode_commas(result)
        explanations = explain.get_explanations(text)

        json.dumps({ 'result': result, 'explanations': explanations }, separators=(',', ':'))
        print(result)