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
    result = {
        'type':    type,
        'change':  change,   
    }

    if explanation:
        result['explain'] = explanation,

    return result