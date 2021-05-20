import spacy
import sys

from enum import Enum

side_words = [
    "og",
    "men",
    "eller",
    "samt",
    "for",
    "thi",
    "både",
]

under_words = [
    "at",
    "da",
    "dengang",
    "end",
    "efter",
    "for",
    "fordi",
    "før",
    "hvorvidt",
    "idet",
    "ifald",
    "indtil",
    "jo",
    "ligesom",
    "medmindre",
    "mens",
    "når",
    "om",
    "selv",
    "siden",
    "skønt",
    "som",
    "så",
    "såfremt",
    "snart",
    "til",
    "uden",
    "ved",
    "m.fl.",
    "selvom",
    "inden",
]

intj_words = ["hallo", "av", "halløj", "hey", "eow", "hej"]

detail_words = [
    "især",
    "men",
    "bare",
    "selvom",
    "dog",
    "herunder",
    "heriblandt",
    "såsom",
    "e.g.",
    "eksempelvis",
    "f.eks.",
]

question_words = [
    "ikke",
]

listing_words = [
    "og",
    "eller",
]


class ClauseType(Enum):
    MAIN = 0  # Helsætning.

    SUB_SIDE = 1  # Sideordnet ledsætning.
    SUB_UNDER = 2  # Underordnet ledsætning.

    ITERATION = 3  # [Ost, løg og ærter]

    IND_DIRECT = 4  # [Per], du lugter.
    IND_ADD = 5  # Jeg hader ost, [især dumme oste].
    IND_APP = 6  # Danmarks hovedstad, [København].
    IND_LIM = 7  # [Av], det gjorde ondt.

    UNKNOWN = 8


def is_whole_sentence(clause):
    subject = False
    root = False

    for tok in clause:
        if tok.dep_ == "ROOT":
            root = True
        if "subj" in tok.dep_:
            subject = True

    return subject and root


def maybe_direct(clause):
    first = clause[0].text.lower()
    poss = list(dict.fromkeys([x.pos_ for x in clause]))

    if poss == ["PROPN"]:
        return ClauseType.IND_DIRECT

    if clause[0].pos_ == "INTJ" or first in intj_words:
        return ClauseType.IND_LIM

    if first in detail_words or len(poss) == 2 and poss[0] in question_words:
        return ClauseType.IND_ADD

    return None


def type_clause(clause):
    clause = list(filter(lambda x: not x.pos_ in ["PUNCT"], clause))

    if len(clause) > 0:

        ### SUBORDINATE CLAUSES ###

        if clause[0].lemma_ in side_words:
            return ClauseType.SUB_SIDE
        if clause[0].lemma_ in under_words:
            return ClauseType.SUB_UNDER

        ### A HELSÆTNING / MAIN CLAUSE ###
        if is_whole_sentence(clause):
            return ClauseType.MAIN

        ### INDEPENDENT CLAUSE ###
        if tp := maybe_direct(clause):
            return tp

    return ClauseType.UNKNOWN


def compare_listing_initial(meta, meta_initial):
    return meta.text == meta_initial.text or meta.tag_ == meta_initial.tag_


def has_listing_potential(clause, nlp):
    for word in listing_words:
        if word in clause:

            if clause.index(word) + 1 < len(clause):
                meta = nlp(clause[clause.index(word) + 1])[0]
                meta_initial = nlp(clause[0])[0]

                if compare_listing_initial(meta, meta_initial):
                    return meta

    return None


def explain_commas(clauses, types, nlp):
    """
    Go through clauses and types in reverse order,
    mapping recurrent and independent types in order
    to an explanations.
    In reverse to grab listings in one go.
    Return:
        exes: List of explanations for each comma.
    """
    exes = []

    if len(types) > 1:
        last = None
        list_meta = None
        was_last_list = False

        for i, (clause, tp) in enumerate(reversed(list(zip(clauses, types)))):
            if last == ClauseType.MAIN and tp == ClauseType.MAIN:
                exes.append("Komma mellem ledsætninger.")

            clause = clause.replace(",", "").strip().split(" ")

            if meta := has_listing_potential(clause, nlp):
                list_meta = meta
                was_last_list = True
                last = tp

                continue

            if list_meta:
                if compare_listing_initial(nlp(clause[0])[0], list_meta):
                    if was_last_list:
                        # exes.append('Komma ved opremsning.')
                        pass

                    exes.append("Komma ved opremsning.")
                    was_last_list = False
                else:
                    list_meta = None

            elif clause[0] in ["der", "som"]:
                exes.append("Komma ved parentetiske relativsætninger.")

            elif tp == ClauseType.SUB_SIDE:
                exes.append("Komma efter sideordnet ledsætning.")

            elif tp == ClauseType.SUB_UNDER:
                exes.append("Komma efter underordnet ledsætning.")

            elif tp == ClauseType.IND_DIRECT:
                exes.append("Komma ved direkte tale.")

            elif tp == ClauseType.IND_APP:
                exes.append("Komma ved parentetiske appositioner.")

            elif tp == ClauseType.IND_ADD:
                exes.append("Komma ved forklaringer og præcisioner.")

            elif tp == ClauseType.IND_LIM:
                exes.append("Komma ved afgrænsning.")

            elif last == ClauseType.SUB_UNDER:
                exes.append("Komma før underordnet ledsætning.")

            elif last == ClauseType.SUB_SIDE:
                exes.append("Komma før sideordnet ledsætning.")
            else:
                exes.append(None)

            last = tp

    return reversed(exes)


def is_action_clause(pos):
    return "VERB" in pos or "AUX" in pos


def get_explanations(text, nlp):
    sents = list(nlp(text).sents)

    exes = []
    types = []
    commas = []

    for sent in sents:
        start = 0
        last_pos = None
        last_tp = None

        for i, j in enumerate(sent):
            if "," in j.text or i == len(sent) - 1:
                if i == len(sent) - 1:
                    i = len(sent)

                clause = sent[start:i]

                if len(str(sent[start : i + 1]).replace(",", "").replace(".", "")) == 0:
                    break

                # Til Niels i fremtiden. :)))
                # Men egentlig er det ikke alene salgsprisens som afgør om en bolig er billig, eller dyr.

                commas.append(" ".join([x.text for x in sent[start:i]]))
                tp = type_clause(sent[start:i])

                pos = [x.pos_ for x in sent[start:i]]

                # If last set as direct, but there is no action here; it was an APP.
                if last_tp == ClauseType.IND_DIRECT and not is_action_clause(pos):
                    types[len(types) - 1] = ClauseType.IND_APP

                if last_pos:
                    # If this is a direct, but had no action befor, this is an APP.
                    if tp == ClauseType.IND_DIRECT and not is_action_clause(last_pos):
                        types.append(ClauseType.IND_APP)
                    else:
                        # It is a direct here.
                        types.append(tp)
                else:
                    # This is the first: go ahead.
                    types.append(tp)

                last_pos = pos
                last_tp = tp
                start = i

        # types.append(type_clause(sent[start:]))
        # commas.append(' '.join([x.text for x in sent[start:]]))

        exes.extend(explain_commas(commas, types, nlp))

    return exes


# Helper functions providing an interface for the diff structure:


def explain(type, original=None, change=None, explanation=None):
    if type == "none":
        return {
            "type": "none",
            "origin": original,
        }
    elif type == "add":
        return {"type": "add", "change": change, "explain": explanation}

    result = {
        "type": type,
        "change": change,
        "origin": original,
    }

    if explanation:
        result["explain"] = explanation

    return result


def change(type, change, explanation=None, origin=""):
    if type in ["none", "space"]:
        return {
            "type": type,
            "origin": change,
        }

    result = {
        "type": type,
        "origin": origin,
        "change": change,
    }

    if explanation:
        result["explain"] = explanation

    return result


def change_map(changes):
    change_map = []
    for i, change in enumerate(changes):
        if change["type"] == "none":
            change_map.append((change["origin"], i, None))
        else:
            content = change["change"]

            if change["type"] == "split":
                change_map.append(
                    (
                        content[0]["type"] == "none"
                        and content[0]["origin"]
                        or content[0]["change"],
                        i,
                        0,
                    )
                )
                change_map.append(
                    (
                        content[1]["type"] == "none"
                        and content[1]["origin"]
                        or content[1]["change"],
                        i,
                        1,
                    )
                )
            else:
                change_map.append((content, i, None))
    return change_map


def insert_change(changes, i, split_i, new_change, explanation):
    if changes[i]["type"] == "none":
        changes[i]["type"] = "replace"
        changes[i]["change"] = new_change["change"]
        changes[i]["explain"] = explanation
    else:
        if changes[i]["type"] == "replace":
            changes[i]["change"] = new_change["change"]

            if type(changes[i]["explain"]) == str:
                changes[i]["explain"] = [changes[i]["explain"], new_change["explain"]]
            else:
                changes[i]["explain"].append(new_change["explain"])

        else:
            # if split_i is None:
            #     split_i = len(changes[i]['change']) - 1

            split_change = changes[i]["change"][split_i]

            if split_change["type"] == "none":
                changes[i]["change"][split_i]["change"] = new_change["change"]
                changes[i]["change"][split_i]["explain"] = new_change["explain"]
            else:
                # If change is a list, explain is as well.
                if type(split_change["explain"]) == str:
                    changes[i]["change"][split_i]["change"] = new_change["change"]

                    changes[i]["change"][split_i]["explain"] = [
                        split_change["explain"],
                        new_change["explain"],
                    ]
                else:
                    changes[i]["change"][split_i]["change"] = new_change["change"]
                    changes[i]["change"][split_i]["explain"].append(explanation)


def insert_push_change(changes, i, split_i, new_change, explanation):
    if changes[i]["type"] == "none":
        changes[i]["type"] = "replace"
        changes[i]["change"] = new_change["change"]
        changes[i]["explain"] = explanation
    elif changes[i]["type"] == "replace":
        changes[i]["change"] = new_change["change"]

        if type(changes[i]["explain"]) == str:
            changes[i]["explain"] = [changes[i]["explain"], new_change["explain"]]
        else:
            changes[i]["explain"].append(new_change["explain"])

    elif changes[i]["type"] == "split":
        # try:
        #     changes[i]["change"][split_i]["change"] = changes[i]["change"][split_i][
        #         "change"
        #     ].split()
        # except:
        #     import pdb

        #     pdb.set_trace()

        changes[i]["change"].insert(split_i + 1, new_change)


if __name__ == "__main__":

    def test_in(exes, text):
        for i, ex in enumerate(get_explanations(text)):
            if len(exes) == i:
                break

            if not exes[i] in ex:
                print(f'Fail: "{exes[i]}" not in "{ex}"', file=sys.stderr)
                sys.exit(1)

            print(f'"{exes[i]}": very nice')

    def tests():
        test_in(["ved opremsning"], "Han elsker kylling, han er sej og han er ost.")
        test_in(
            ["ved parentetiske relativsætninger"], "ham manden, der er en gangster."
        )
        test_in(["ved direkte tale"], "Niels, du er en gangster.")
        test_in(["ved parentetiske appositioner"], "Danmarks hovedstad, Køkenhavn")
        test_in(["ved forklaringer og præcisioner"], "Orto er god, især til kommaer.")
        test_in(["ved afgrænsning"], "Av, det gjorde godt nok ondt.")
        test_in(["før underordnet ledsætning"], "Det var fedt, dengang jeg var lille.")
        test_in(["før sideordnet"], "kyllingen er stærk, men den er dum.")

        print("\n==== Tests passed: feel good time. ====\n")

    if sys.argv[1] == "test":
        tests()

    while True:
        text = input("> ")
        print(get_explanations(text))
        print()
