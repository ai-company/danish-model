def explain(type, original, correct=None, explanation=None):
    if type == 'none':
        return {
            'type': 'none',
            'origin': original,
        }

    result = {
        'type':    type,
        'change':  correct,
        'origin':  original,
    }

    if explanation:
        result['explain'] = explanation,

    return result


def change(type, change, explanation):
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
