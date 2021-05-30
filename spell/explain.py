def explain(ctype, original, correct=None, explanation=None):
    if ctype == "none":
        return {
            "type": "none",
            "origin": original,
        }
    elif ctype == "split" and type(correct) == str:
        result = []

        parts = correct.split(" ")
        for i, t in enumerate(parts):
            if i < len(parts) - 1:
                t += " "

            result.append(change("none", t))

        correct = result

    result = {
        "type": ctype,
        "change": correct,
        "origin": original,
    }

    if explanation:
        result["explain"] = explanation if type(explanation) is list else [explanation]

    return result


def change(type, change, explanation=None):
    if type == "none":
        return {
            "type": "none",
            "origin": change,
        }

    result = {
        "type": type,
        "change": change,
    }

    if explanation:
        result["explain"] = [explanation]

    return result


def append_change(changes, i, change):
    if changes[i]["type"] == "none":
        changes[i]["type"] == "replace"

        changes[i]["change"] = change["change"]
    else:
        if type(changes[i]["change"]) == str:
            changes[i]["change"] = [changes[i]["change"], change]
        else:
            changes[i]["change"].append(change)


def change_map(changes):
    change_map = []
    for i, change in enumerate(changes):
        if change["type"] == "none" or change["type"] == "space":
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


def insert_append_change(changes, i, split_i, new_change, explanation):
    if changes[i]["type"] == "none":
        changes[i]["change"] = new_change["change"]
        changes[i]["type"] = "replace"
        changes[i]["explain"] = explanation
    elif changes[i]["type"] == "replace":
        changes[i]["change"] = new_change["change"]

        if type(changes[i]["explain"]) == str:
            changes[i]["explain"] = [changes[i]["explain"], new_change["explain"]]
        else:
            changes[i]["explain"].append(new_change["explain"])

    elif changes[i]["type"] == "split":
        # if split_i is None:
        #     split_i = len(changes[i]['change']) - 1

        split_change = changes[i]["change"][split_i]

        if split_change["type"] == "none":
            changes[i]["change"][split_i]["change"] = new_change
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
