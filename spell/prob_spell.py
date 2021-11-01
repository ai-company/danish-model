from .distance import distance as damerau_levenshtein_distance
from collections import defaultdict, namedtuple
from itertools import cycle
from .explain import explain, change
from os.path import join, dirname

import sys
import os
import re
import math
import string
import lemmy

from . import util
from . import test

from spell.compound import BINDINGS, COMPOUNDABLE

from diff_token import tokenize, LexemeType

# Preload lemmy
# TODO: Make one lemmy instance somewhere maybe.
lemmatizer = lemmy.load("da")


def is_acronym(word, match_digits=False):
    if match_digits:
        return any(i.isdigit() for i in word)

    return re.match(r"\b[A-Z0-9]{2,}\b", word) is not None


class Spell:
    bigram_count_min = sys.maxsize
    N = 230479668  # smol boi

    def __init__(self, max_dict_edit_dist=2, prefix_len=7, count_threshold=1):
        self.words = dict()
        self.below_threshold_words = dict()
        self.bigrams = dict()
        self.deletes = defaultdict(list)
        self.max_dict_edit_dist = max_dict_edit_dist
        self.prefix_len = prefix_len
        self.max_length = 0
        self.replaced_words = dict()
        self.count_threshold = count_threshold

    def create_dict_entry(self, key, count):
        if count <= 0:
            if self.count_threshold > 0:
                return False
            count = 0

        if self.count_threshold > 1 and key in self.below_threshold_words:
            count_previous = self.below_threshold_words[key]

            count = (
                count_previous + count
                if sys.maxsize - count_previous > count
                else sys.maxsize
            )

            if count >= self.count_threshold:
                self.below_threshold_words.pop(key)
            else:
                self.below_threshold_words[key] = count
                return False

        elif key in self.words:
            count_previous = self.words[key]

            count = (
                count_previous + count
                if sys.maxsize - count_previous > count
                else sys.maxsize
            )

            self.words[key] = count
            return False
        elif count < self.count_threshold:
            self.below_threshold_words[key] = count
            return False

        self.words[key] = count

        if len(key) > self.max_length:
            self.max_length = len(key)

        edits = self.edits_prefix(key)

        for delete in edits:
            self.deletes[delete].append(key)

        return True

    def delete_dict_entry(self, key):
        if key not in self.words:
            return False

        del self.words[key]

        if len(key) == self.max_length:
            self.max_length = max(map(len, self.words.keys()))

        edits = self.edits_prefix(key)

        for delete in edits:
            self.deletes[delete].remove(key)

        return True

    def load_bigram_dict(
        self, corpus_path, term_index, count_index, sep=None, encoding=None
    ):
        if not os.path.exists(corpus_path):
            return False

        with open(corpus_path, "r", encoding=encoding) as f:
            return self.load_bigram_dict_stream(f, term_index, count_index, sep)

    def load_bigram_dict_stream(
        self, corpus_stream, term_index=None, count_index=None, sep=None
    ):
        min_line_parts = 3 if sep is None else 2

        for line in corpus_stream:
            line_parts = line.rstrip().split(sep)

            if len(line_parts) >= min_line_parts:
                key = f"{line_parts[term_index]}{line_parts[term_index + 1]}"
                count = util.parse_int64(line_parts[count_index])

                if count is not None:
                    self.bigrams[key] = count
                    if count < self.bigram_count_min:
                        self.bigram_count_min = count

        return True

    def load_dict(self, corpus_path, term_index, count_index, sep=" ", encoding=None):
        if not os.path.exists(corpus_path):
            return False

        with open(corpus_path, "r", encoding=encoding) as f:
            return self.load_dict_stream(f, term_index, count_index, sep)

    def load_dict_stream(self, corpus_stream, term_index, count_index, sep=" "):
        for line in corpus_stream:
            line_parts = line.rstrip().split(sep)

            if len(line_parts) >= 2:
                key = line_parts[term_index]
                count = util.parse_int64(line_parts[count_index])

                if count is not None:
                    self.create_dict_entry(key, count)

        return True

    def create_dict(self, corpus: str, encoding=None):
        if not os.path.exists(corpus):
            return False

        with open(corpus, "r", encoding=encoding) as f:
            for line in f:
                for key in self.parse_words(line):
                    self.create_dict_entry(key, 1)

        return True

    def lookup(self, phrase, max_edit_dist=2, closeness="*", include_unknown=False):
        if max_edit_dist is None:
            max_edit_dist = self.max_dict_edit_dist

        suggestions = list()
        phrase_len = len(phrase)

        def early():
            if include_unknown and not suggestions:
                suggestions.append(Suggestion(phrase, max_edit_dist + 1, 0))

            return suggestions

        if phrase_len - max_edit_dist > self.max_length:
            return early()

        suggestion_count = 0

        phrase_lemma = lemmatizer.lemmatize('', phrase)[0]
        phrase_exists = phrase in self.words

        if phrase_exists or phrase_lemma in self.words:
            word = phrase_exists and phrase or phrase_lemma

            suggestion_count = self.words[word]
            suggestions.append(Suggestion(phrase, 0, suggestion_count))

            if closeness != "*":
                return early()

        if max_edit_dist == 0:
            return early()

        considered_deletes = set()
        considered_suggestions = set()

        considered_suggestions.add(phrase)

        max_edit_dist2 = max_edit_dist
        candidate_pointer = 0
        candidates = list()

        phrase_prefix_len = phrase_len

        if phrase_prefix_len > self.prefix_len:
            phrase_prefix_len = self.prefix_len
            candidates.append(phrase[:phrase_prefix_len])
        else:
            candidates.append(phrase)

        while candidate_pointer < len(candidates):
            candidate = candidates[candidate_pointer]
            candidate_pointer += 1
            candidate_len = len(candidate)
            len_diff = phrase_prefix_len - candidate_len

            if len_diff > max_edit_dist2:
                if closeness == "*":
                    continue

                break

            if candidate in self.deletes:
                dict_suggestions = self.deletes[candidate]
                for suggestion in dict_suggestions:
                    if suggestion == phrase:
                        continue

                    suggestion_len = len(suggestion)

                    if (
                        abs(suggestion_len - phrase_len) > max_edit_dist2
                        or suggestion_len < candidate_len
                        or (suggestion_len == candidate_len and suggestion != candidate)
                    ):
                        continue

                    suggestion_prefix_len = min(suggestion_len, self.prefix_len)

                    if (
                        suggestion_prefix_len > phrase_prefix_len
                        and suggestion_prefix_len - candidate_len > max_edit_dist2
                    ):
                        continue

                    distance = 0
                    min_dist = 0

                    if candidate_len == 0:
                        distance = max(phrase_len, suggestion_len)
                        if (
                            distance > max_edit_dist2
                            or suggestion in considered_suggestions
                        ):
                            continue

                    elif suggestion_len == 1:
                        distance = (
                            phrase_len
                            if phrase.index(suggestion[0]) < 0
                            else phrase_len - 1
                        )
                        if (
                            distance > max_edit_dist2
                            or suggestion in considered_suggestions
                        ):
                            continue
                    else:
                        if self.prefix_len - max_edit_dist == candidate_len:
                            min_dist = min(phrase_len, suggestion_len) - self.prefix_len
                        else:
                            min_dist = 0

                        if (
                            self.prefix_len - max_edit_dist == candidate_len
                            and (
                                min_dist > 1
                                and phrase[phrase_len + 1 - min_dist :]
                                != suggestion[suggestion_len + 1 - min_dist :]
                            )
                            or (
                                min_dist > 0
                                and phrase[phrase_len - min_dist]
                                != suggestion[suggestion_len - min_dist]
                                and (
                                    phrase[phrase_len - min_dist - 1]
                                    != suggestion[suggestion_len - min_dist]
                                    or phrase[phrase_len - min_dist]
                                    != suggestion[suggestion_len - min_dist - 1]
                                )
                            )
                        ):
                            continue
                        elif suggestion in considered_suggestions:
                            continue

                        considered_suggestions.add(suggestion)

                        distance = damerau_levenshtein_distance(
                            phrase, suggestion, max_edit_dist2
                        )

                        if distance < 0:
                            continue

                    if distance <= max_edit_dist2:
                        suggestion_count = self.words[suggestion]
                        si = Suggestion(suggestion, distance, suggestion_count)

                        if suggestions:
                            if closeness == "top":
                                if (
                                    distance < max_edit_dist2
                                    or suggestion_count > suggestions[0].count
                                ):
                                    max_edit_dist2 = distance
                                    suggestions[0] = si

                                continue

                        if closeness != "*":
                            max_edit_dist2 = distance

                        suggestions.append(si)

            if len_diff < max_edit_dist and candidate_len <= self.prefix_len:
                if closeness != "*" and len_diff >= max_edit_dist2:
                    continue

                for i in range(candidate_len):
                    delete = candidate[:i] + candidate[i + 1 :]
                    if delete not in considered_deletes:
                        considered_deletes.add(delete)
                        candidates.append(delete)

        if len(suggestions) > 1:
            suggestions.sort()

        early()
        return suggestions

    def is_actually_ok(self, word, nlp):
        pos = nlp(word)[0].pos_
        if word not in self.words:
            return (
                word.endswith("'s")
                and word[:-2] in self.words
                and pos.lower() in ["noun", "propn"]
            )
        else:
            return True

    def lookup_compound(
        self,
        phrase,
        upper_mask,
        max_edit_dist=2,
        split_space=False,
        ignore_non_words=False,
        nlp=None,
        corpus=None
    ):
        term_list = util.parse_words(phrase, split_space, nlp)
        explanations = []

        if ignore_non_words:
            term_list2 = util.parse_words(phrase, split_space, nlp)

        suggestions = list()
        suggestion_parts = list()

        is_last_combi = False

        for i, word in enumerate(term_list):
            token = tokenize(word)[0]

            if token.lexeme.type != LexemeType.WORD or self.is_actually_ok(
                word, nlp
            ) or (i < len(upper_mask) and upper_mask[i]):
                suggestion_parts.append(Suggestion(term_list[i], 0, 0))
                continue

            # TODO: Think very fucking hard.
            if len(word) == 1 and not word.isalnum():  # test.is_deep_real(word):
                suggestion_parts.append(Suggestion(term_list[i], 0, 0))
                continue

            if ignore_non_words:
                if util.parse_int64(term_list[i]) is not None:
                    suggestion_parts.append(Suggestion(term_list[i], 0, 0))
                    continue

                if is_acronym(term_list2[i], match_digits=False):
                    suggestion_parts.append(Suggestion(term_list2[i], 0, 0))
                    continue

            suggestions = self.lookup(term_list[i], max_edit_dist, closeness="top")

            if i > 0 and not is_last_combi:
                suggestion_combi = self.lookup(
                    term_list[i - 1] + term_list[i], max_edit_dist, closeness="top"
                )

                if suggestion_combi:
                    best1 = suggestion_parts[-1]

                    if suggestions:
                        best2 = suggestions[0]
                    else:
                        best2 = Suggestion(
                            term_list[i],
                            max_edit_dist + 1,
                            10 // 10 ** len(term_list[i]),
                        )

                    distance1 = best1.distance + best2.distance

                    if distance1 >= 0 and (
                        suggestion_combi[0].distance + 1 < distance1
                        or (
                            suggestion_combi[0].distance + 1 == distance1
                            and (
                                suggestion_combi[0].count
                                > best1.count / self.N * best2.count
                            )
                        )
                    ):

                        suggestion_combi[0].distance += 1
                        suggestion_parts[-1] = suggestion_combi[0]

                        is_last_combi = True

                        continue

            is_last_combi = False

            if suggestions and (suggestions[0].distance == 0 or len(term_list[i]) == 1):
                suggestion_parts.append(suggestions[0])
            else:
                suggestion_split_best = None

                if suggestions:
                    suggestion_split_best = suggestions[0]

                if len(term_list[i]) > 1:
                    for j in range(1, len(term_list[i])):
                        part1 = term_list[i][:j]
                        part2 = term_list[i][j:]

                        suggestion1 = self.lookup(part1, max_edit_dist, closeness="top")

                        if suggestion1:
                            suggestion2 = self.lookup(
                                part2, max_edit_dist, closeness="top"
                            )

                            if suggestion2:
                                tmp_term = (
                                    suggestion1[0].term + " " + suggestion2[0].term
                                )
                                # TODO: check if we can get the edit list, to know which halves of the word are correct
                                # TODO: potential alternative: try matching word start/end in the resulting correction
                                # TODO:     to find the approximate position, and also match capitalization
                                tmp_dist = damerau_levenshtein_distance(
                                    term_list[i], tmp_term, max_edit_dist
                                )

                                if tmp_dist < 0:
                                    tmp_dist = max_edit_dist + 1

                                if suggestion_split_best is not None:
                                    if tmp_dist > suggestion_split_best.distance:
                                        continue

                                    if tmp_dist < suggestion_split_best.distance:
                                        suggestion_split_best = None

                                if tmp_term in self.bigrams:
                                    tmp_count = self.bigrams[tmp_term]

                                    if suggestions:
                                        best_s = suggestions[0]

                                        if (
                                            suggestion1[0].term + suggestion2[0].term
                                            == term_list[i]
                                        ):
                                            tmp_count = max(tmp_count, best_s.count + 2)
                                        elif (
                                            suggestion1[0].term == best_s.term
                                            or suggestion2[0].term == best_s.term
                                        ):
                                            tmp_count = max(tmp_count, best_s.count + 1)

                                    elif (
                                        suggestion1[0].term + suggestion2[0].term
                                        == term_list[i]
                                    ):
                                        tmp_count = max(
                                            tmp_count,
                                            max(
                                                suggestion1[0].count,
                                                suggestion2[0].count,
                                            )
                                            + 2,
                                        )
                                else:
                                    tmp_count = min(
                                        self.bigram_count_min,
                                        suggestion1[0].count
                                        // self.N
                                        * suggestion2[0].count,
                                    )

                                suggestion_split = Suggestion(
                                    tmp_term, tmp_dist, tmp_count
                                )

                                if (
                                    suggestion_split_best is None
                                    or suggestion_split.count
                                    > suggestion_split_best.count
                                ):
                                    suggestion_split_best = suggestion_split

                    if suggestion_split_best is not None:
                        suggestion_parts.append(suggestion_split_best)
                        self.replaced_words[term_list[i]] = suggestion_split_best
                    else:
                        s = Suggestion(
                            term_list[i],
                            max_edit_dist + 1,
                            10 // 10 ** len(term_list[i]),
                        )
                        suggestion_parts.append(s)

                        self.replaced_words[term_list[i]] = s
                else:
                    s = Suggestion(
                        term_list[i], max_edit_dist + 1, 10 // 10 ** len(term_list[i])
                    )
                    suggestion_parts.append(s)

                    self.replaced_words[term_list[i]] = s

        joined_term = ""
        joined_count = self.N

        for i, s in enumerate(suggestion_parts):
            split = s.term.split()

            if tokenize(s.term)[0].lexeme.type != LexemeType.WORD:
                explanations.append(explain("none", s.term))
            else:
                if len(split) > 1:
                    abort_mission = False
                    for bind in ['s', 'e']:
                        c = term_list[i].split(bind)
                        
                        if False and len(c) > 1 and c[0] in corpus and c[1] in corpus:
                            explanations.append(explain("none", c[0] + bind + c[1]))
                            abort_mission = True

                    one_in = split[0] in term_list[i]
                    two_in = split[1] in term_list[i]


                    #for binding in BINDINGS:
                    #    if (
                    #        nlp(split[0])[0].pos_.lower() in COMPOUNDABLE
                    #        and nlp(split[1])[0].pos_.lower() in COMPOUNDABLE
                    #    ):
                    #        if (origin := split[0] + binding + split[1]) == term_list[
                    #            i
                    #        ]:
                    #            explanations.append(explain("none", origin))
                    #            abort_mission = True

                    #            break

                    if not abort_mission:
                        if one_in and two_in:
                            explanations.append(
                                explain(
                                    "split",
                                    term_list[i],
                                    s.term,
                                    "Ordet bør opdeles i flere.",
                                )
                            )
                        else:
                            explanation = "Ordet var oprindeligt stavet forkert."
                            changes = [
                                change(
                                    one_in and "none" or "replace",
                                    split[0] + " ",
                                    one_in and None or explanation,
                                ),
                                change(
                                    two_in and "none" or "replace",
                                    split[1],
                                    two_in and None or explanation,
                                ),
                            ]

                            explanations.append(
                                explain(
                                    "split",
                                    term_list[i],
                                    changes,
                                    "Ordet bør opdeles i flere",
                                )
                            )
                else:
                    if s.term == term_list[i]:
                        explanations.append(explain("none", s.term))
                    else:
                        if s.term + '-' == term_list[i]:
                            explanations.append(explain("none", s.term + '-'))
                        else:
                            explanations.append(
                                explain(
                                    "replace",
                                    term_list[i],
                                    s.term,
                                    "Ordet var oprindeligt stavet forkert.",
                                )
                            )

            joined_term += s.term + " "
            joined_count *= s.count / self.N

        joined_term = joined_term.rstrip()

        suggestion = Suggestion(
            joined_term,
            damerau_levenshtein_distance(phrase, joined_term, 2 ** 31 - 1),
            int(joined_count),
        )
        suggestion_line = list()

        suggestion_line.append(suggestion)

        return suggestion_line, explanations

    def segmentation(self, phrase, max_edit_dist=None, max_segmentation_len=None):
        if max_edit_dist is None:
            max_edit_dist = self.max_dict_edit_dist

        if max_segmentation_len is None:
            max_segmentation_len = self.max_length

        array_size = min(max_segmentation_len, len(phrase))
        compositions = [Composition()] * array_size
        circular_index = cycle(range(array_size))

        idx = -1

        for j in range(len(phrase)):
            imax = min(len(phrase) - j, max_segmentation_len)

            for i in range(1, imax + 1):
                part = phrase[j : j + i]
                sep_len = 0

                top_ed = 0
                top_log_prob = 0.0
                top_result = ""

                if part[0].isspace():
                    part = part[1:]
                else:
                    sep_len = 1

                top_ed += len(part)

                part = part.replace(" ", "")
                top_ed -= len(part)
                results = self.lookup(part.lower(), max_edit_dist, closeness="top")

                if results:
                    top_result = results[0].term

                    if len(part) > 0 and part[0].isupper():
                        top_result = top_result.capitalize()

                    top_ed += results[0].distance
                    top_log_prob = math.log10(float(results[0].count) / float(self.N))
                else:
                    top_result = part
                    top_ed += len(part)

                    top_log_prob = math.log10(10.0 / self.N / math.pow(10.0, len(part)))

                dest = (i + idx) % array_size

                comp = compositions[idx]

                if j == 0:
                    compositions[dest] = Composition(
                        part, top_result, top_ed, top_log_prob
                    )
                elif (
                    i == max_segmentation_len
                    or (
                        (
                            comp.distance_sum + top_ed
                            == compositions[dest].distance_sum
                            or comp.distance_sum + sep_len + top_ed
                            == compositions[dest].distance_sum
                        )
                        and compositions[dest].log_prob_sum
                        < comp.log_prob_sum + top_log_prob
                    )
                    or comp.distance_sum + sep_len + top_ed
                    < compositions[dest].distance_sum
                ):

                    if (
                        len(top_result) == 1 and top_result[0] in string.punctuation
                    ) or (len(top_result) == 2 and top_result.startswith("'")):

                        compositions[dest] = Composition(
                            comp.segmented_string + part,
                            comp.corrected_string + top_result,
                            comp.distance_sum + top_ed,
                            comp.log_prob_sum + top_log_prob,
                        )
                    else:
                        compositions[dest] = Composition(
                            comp.segmented_string + " " + part,
                            comp.corrected_string + " " + top_result,
                            comp.distance_sum + sep_len + top_ed,
                            comp.log_prob_sum + top_log_prob,
                        )

            idx = next(circular_index)

        return compositions[idx]

    def edits(self, word, edit_dist, delete_words):
        edit_dist += 1
        word_len = len(word)

        if word_len > 1:
            for i in range(word_len):
                delete = word[:i] + word[i + 1 :]

                if delete not in delete_words:
                    delete_words.add(delete)

                    if edit_dist < self.max_dict_edit_dist:
                        self.edits(delete, edit_dist, delete_words)

        return delete_words

    def edits_prefix(self, key):
        hash_set = set()

        if len(key) <= self.max_dict_edit_dist:
            hash_set.add("")

        if len(key) > self.prefix_len:
            key = key[: self.prefix_len]

        hash_set.add(key)

        return self.edits(key, 0, hash_set)

    # capitalization dies here
    def parse_words(self, text):
        matches = re.findall(r"(([^\W_]|[\'’])+)", text.lower())
        matches = [match[0] for match in matches]

        return matches


Composition = namedtuple(
    "Composition",
    ["segmented_string", "corrected_string", "distance_sum", "log_prob_sum"],
)
Composition.__new__.__defaults__ = (None,) * len(Composition._fields)


class Suggestion:
    def __init__(self, term, distance, count):
        self.term = term
        self.distance = distance
        self.count = count

    def __eq__(self, other):
        if self.distance == other.distance:
            return self.count == other.count
        else:
            return self.distance == other.distance

    def __lt__(self, other):
        if self.distance == other.distance:
            return self.count > other.count
        else:
            return self.distance < other.distance

    def __str__(self):
        return self.term


def init():
    s = Spell()
    s.load_dict(join(dirname(__file__), "dictionary.txt"), 0, 1, sep=" ")
    s.load_bigram_dict(join(dirname(__file__), "bigrams.txt"), 0, 2, sep=" ")

    def process(text, upper_mask, nlp, corpus_words):
        """
        Processes a sentence, fixing spelling and wrongly mixed words.

        Params:
            - text: The sentence to be processed.
        """

        return s.lookup_compound(text, upper_mask, max_edit_dist=2, nlp=nlp, corpus=corpus_words)

    return process

if __name__ == "__main__":
    spell = init()
    while True:
        text = input("> ")
        spell(text)
