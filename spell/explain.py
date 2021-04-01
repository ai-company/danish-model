def explain(type, original, correct=None, explanation=None):
    if type == 'none':
        return {
            'type': 'none',
            'origin': original,
        }
    elif type == 'split' and type(correct) == str:
        correct = [change('none', t) for t in list(correct.split(' '))]

    result = {
        'type':    type,
        'change':  correct,
        'origin':  original,
    }

    if explanation:
        result['explain'] = explanation,

    return result


def change(type, change, explanation=None):
    if type == 'none':
        return {
            'type': 'none',
            'origin': change,
        }

    result = {
        'type':    type,
        'change':  change,
    }

    if explanation:
        result['explain'] = explanation,

    return result


def append_change(changes, i, change):
    if changes[i]['type'] == 'none':
        changes[i]['type'] == 'change'

        changes[i]['change'] = [change]
    else:
        if type(changes[i]['change']) == str:
            changes[i]['change'] = [
                changes[i]['change'],
                change
            ]
        else:
            changes[i]['change'].append(change)


def change_map(changes):
    change_map = []
    for i, change in enumerate(changes):
        if change['type'] == 'none':
            change_map.append((change['origin'], i, None))
        else:
            content = change['change']

            if change['type'] == 'split':
                change_map.append(
                    (content[0]['type'] == 'none' and content[0]['origin'] or content[0]['change'], i, 0))
                change_map.append(
                    (content[1]['type'] == 'none' and content[1]['origin'] or content[1]['change'], i, 1))
            else:
                change_map.append((content, i, None))
    return change_map


def insert_change(changes, i, split_i, new_change, explanation):
    if changes[i]['type'] == 'none':
        changes[i]['change'] = new_change
        changes[i]['type'] = 'replace'
    elif changes[i]['type'] == 'replace':
        changes[i]['change'] = [
            change('replace', changes[i]['change'], changes[i]['explain']),
            new_change
        ]

        del changes[i]['explain']
    elif changes[i]['type'] == 'split':
        # if split_i is None:
        #     split_i = len(changes[i]['change']) - 1

        split_change = changes[i]['change'][split_i]
        if split_change['type'] == 'none':
            changes[i]['change'][split_i] = new_change
        else:
            changes[i]['change'][split_i]['change'] = token

            if type(split_change['explain']) == str:
                changes[i]['change'][split_i] = [
                    split_change['explain'],
                    explanation
                ]
            else:
                changes[i]['change'][split_i]['explain'].append(
                    explanation)


def insert_append_change(changes, i, split_i, new_change, explanation):
    if changes[i]['type'] == 'none':
        changes[i]['change'] = new_change
        changes[i]['type'] = 'replace'
    elif changes[i]['type'] == 'replace':
        changes[i]['change'] = [
            changes[i]['change'],
            new_change
        ]

    elif changes[i]['type'] == 'split':
        # if split_i is None:
        #     split_i = len(changes[i]['change']) - 1

        split_change = changes[i]['change'][split_i]
        if split_change['type'] == 'none':
            changes[i]['change'][split_i] = new_change
        else:
            changes[i]['change'][split_i]['change'] = token

            if type(split_change['explain']) == str:
                changes[i]['change'][split_i] = [
                    split_change['explain'],
                    explanation
                ]
            else:
                changes[i]['change'][split_i]['explain'].append(
                    explanation)
