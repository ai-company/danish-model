# coding: utf-8

from __future__ import division
from pprint import pprint
from typing import List
from diff_token import DiffPunc, DiffToken, LexemeType, tokenize
import sys
from os.path import join, dirname
import collections
import json
import re
import tensorflow as tf
import numpy as np
import spacy
from pysbd.utils import PySBDFactory

from . import convert, explain, model, data, clauses
from .config import MINIBATCH_SIZE


def parse_words(phrase, split_space=False):
    if split_space:
        return phrase.split()
    else:
        return re.findall(r"(\w+|[()\[\]{}/_:\|~+\*\^@$#£\.&\-'?!_\>\<])", phrase)


def make_tag(t):
    result = ""

    t = t.split("__")

    result += t[0][:2]

    t = str(t[1:]).split("|")

    hash = {}

    for n in t:
        if "=" in n:
            ass = n.split("=")
            hash[ass[0]] = ass[1]

    hash = collections.OrderedDict(sorted(hash.items()))
    result += "".join([v[0] for _, v in hash.items()])

    return result


def to_array(arr, dtype=np.int32):
    return np.array([arr], dtype=dtype).T


def convert_punctuation_to_readable(punct_token):
    if punct_token == data.SPACE:
        return " "
    else:
        return punct_token[0]


def punctuate(
    word_vocabulary, punctuation_vocabulary, reverse_punctuation_vocabulary, text, model
):
    if len(text) == 0:
        return ""

    text = [w for w in text.split() if w not in punctuation_vocabulary] + [data.END]
    i = 0

    result = ""

    while True:
        subsequence = text[i : i + data.MAX_SEQUENCE_LEN]

        if len(subsequence) == 0:
            break

        converted_subsequence = [
            word_vocabulary.get(w, word_vocabulary[data.UNK]) for w in subsequence
        ]

        y = predict(to_array(converted_subsequence), model)

        last_eos_idx = 0
        punctuations = []
        for y_t in y:
            p_i = np.argmax(tf.reshape(y_t, [-1]))

            punctuation = reverse_punctuation_vocabulary[
                min(p_i, len(reverse_punctuation_vocabulary) - 1)
            ]

            punctuations.append(punctuation)

            if punctuation in data.EOS_TOKENS:
                last_eos_idx = len(punctuations)

        if subsequence[-1] == data.END:
            step = len(subsequence) - 1
            # print(f'step END: {step}')
        elif last_eos_idx != 0:
            step = last_eos_idx
            # print(f'step eos: {step}')
        else:
            step = len(subsequence) - 1
            # print(f'step subseq: {step}')

        token = ""

        for j in range(step):
            if j > 0:
                token += " "

            token = punctuations[j] + " " if punctuations[j] != data.SPACE else " "
            result += token

            if j < step:
                result += subsequence[1 + j]

        if subsequence[-1] == data.END:
            break

        i += step
        # print(f'jumping i: {i}')

    return " ".join(result.split()[:-1])


def predict(x, model):
    return tf.nn.softmax(model(x))


def init(nlp):
    """
    Comma correction factory; loading models and returning closure for commarization.

    Returns:
        - process: Closure for processing/commarization.
    """

    model_file = join(dirname(__file__), "data/model.pcl")

    vocab_len = len(data.read_vocabulary(data.WORD_VOCAB_FILE))
    x_len = (
        vocab_len
        if vocab_len < data.MAX_WORD_VOCABULARY_SIZE
        else data.MAX_WORD_VOCABULARY_SIZE + data.MIN_WORD_COUNT_IN_VOCAB
    )
    x = np.ones((x_len, MINIBATCH_SIZE)).astype(int)

    net, _ = model.load(model_file, x)

    word_vocabulary = net.x_vocabulary
    punctuation_vocabulary = net.y_vocabulary
    reverse_punctuation_vocabulary = {v: k for k, v in net.y_vocabulary.items()}

    def commarize_sentence(text):
        # if len(text.strip()) == 0:
        #     return ""

        encoded_text = " ".join([make_tag(t.tag_) for t in nlp(text)]).lower()

        result = punctuate(
            word_vocabulary,
            punctuation_vocabulary,
            reverse_punctuation_vocabulary,
            encoded_text,
            net,
        )

        result = result.replace("?QUESTIONMARK", "")

        result = f'{encoded_text.split(" ")[0]} {result}'
        result = convert.convert(result, text, nlp)
        result = f"{result[0].upper()}{result[1:]}"

        return result

    def process(diff, text):
        """
        Text processing closure for commarizing and explaining fixes.

        Params:
            - text: Text to be processed.
            - changes: A reference to incremental changelog.

        Returns:
            - result: The processed text.
            - changes: Updated list of explanations for changes made to the input text.
        """

        if len(text.strip()) == 0:
            return DiffToken.from_spacy_list(nlp(text)), text

        new_text = clauses.heuristics(nlp(commarize_sentence(text)), diff, nlp)

        # print('---')
        # pprint(new_text)

        # Add last period.
        # if new_text[-1] not in ".?!:":
        #     if new_text[-1] == ",":
        #         new_text = new_text[:-1] + "."
        #     else:
        #         new_text += "."

        # the model sometimes inserts a duplicate comma, if there is one already there
        # new_text = re.sub(",+", ",", new_text)
        # pprint(new:_text)

        explanations = explain.get_explanations(new_text, nlp)

        new_text_tokens = DiffToken.from_spacy_list(nlp(new_text))

        # reconcile diffs -------------------------------------

        new_changes: List[DiffToken] = []
        default_explanation = ["Der bør være et komma her."]
        i = j = 0
        while i < len(diff) and j < len(new_text_tokens):
            if diff[i].lexeme.type == new_text_tokens[j].lexeme.type and (
                (
                    diff[i].lexeme.type == LexemeType.PUNC
                    and diff[i].lexeme.text == new_text_tokens[j].lexeme.text
                )
                or (diff[i].lexeme.type != LexemeType.PUNC)
            ):
                # print(f"match: '{diff[i]}' '{new_text_tokens[j]}' ")
                new_changes.append(diff[i].clone_clean())
                i += 1
                j += 1

            else:
                if (
                    diff[i].lexeme.type == LexemeType.PUNC
                    and diff[i].lexeme.text == ","
                ):
                    # punctuation removal
                    # print(f"remove: '{diff[i]}' '{new_text_tokens[j]}' ")
                    i += 1
                elif (
                    new_text_tokens[j].lexeme.type == LexemeType.PUNC
                    and new_text_tokens[j].lexeme.text == ","
                ):
                    # punctuation addition
                    # print(f"add: '{diff[i]}' '{new_text_tokens[j]}' ")
                    explanation = (
                        explanations.pop(0) or default_explanation
                        if len(explanations) > 0
                        else default_explanation
                    )
                    space = new_changes[-1].strip()
                    new_changes.append(
                        DiffPunc(
                            ",", None, explanation, space, None, "add", "," + space
                        )
                    )
                    j += 1
                else:
                    pprint(diff)
                    pprint(new_text_tokens)
                    print(i, diff[i], j, new_text_tokens[j])

                    import pdb
                    pdb.set_trace()

                    raise Exception("unreachable!")

        if i < len(diff):
            print(f"{i}: {len(diff)} | {j}: {len(new_text_tokens)}")
            pprint(diff)
            pprint(new_text_tokens)
            raise Exception("non-exhaustive match of tokens!")

        first_change = new_changes[0]
        i = 0

        while first_change.lexeme.type == LexemeType.SPAC:
            i += 1
            first_change = new_changes[i]

        last_change = new_changes[-1]

        # check first word capitalization
        if (
            first_change.lexeme.text[0].isalpha()
            and not first_change.lexeme.text[0].isupper()
        ):
            first_change.lexeme.text = (
                first_change.lexeme.text[0].upper() + first_change.lexeme.text[1:]
            )
            first_change.explanation.append("Stort begyndelsesbogstav.")
            first_change.change_type = "replace"
            first_change.change = str(first_change.lexeme)

        # check sentence termination
        if (
            last_change.lexeme.type != LexemeType.PUNC
            or last_change.lexeme.text[-1] not in ".!?:"
        ):
            if (
                last_change.lexeme.text == '"' or last_change.change_type == "space"
            ) and not new_changes[-2].lexeme.text[-1] in ".!?:":
                new_changes.insert(
                    -1,
                    DiffPunc(
                        ".",
                        None,
                        ["Sætningen bør afsluttes med et punktum."],
                        "",
                        None,
                        "add",
                        ".",
                    ),
                )

            elif not last_change.lexeme.text[-1] in ".!?:":
                new_changes.append(
                    DiffPunc(
                        ".",
                        None,
                        ["Sætningen bør afsluttes med et punktum."],
                        "",
                        None,
                        "add",
                        ".",
                    )
                )
                if last_change.change_type != "space":
                    new_changes[-1].lexeme.space = last_change.strip()

        return new_changes, "".join(map(str, new_changes))

    return process
