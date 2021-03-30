from transformers import pipeline
from .prob_spell import init
from nltk.corpus import words as corpus_words

from . import explain
from os.path import join, dirname

corpus_words = []

with open(join(dirname(__file__), 'dictionary.txt'), 'r') as f:
    for line in f:
        corpus_words.append(line.split()[0])

unmasker = pipeline('fill-mask', model='Maltehb/danish-bert-botxo')
prob_spell = init()

# TODO: Move to CSV :)
letter_mix_map = {
    'rd': 'r',
    'tt': 't',
    't':  'tt',
    'n':  'nd',
    'nd': 'n',
    'l': 'll',
}

common_spelling_mistakes = dict()


def is_real(word):
    return word in corpus_words


def low_hanging_fruits(sentence):
    words = sentence.split(' ')

    for i, word in enumerate(words):
        if i < len(words) - 2 and len(words) > 1:
            bigram = f'{word} {words[i + 1]}'

            if result := common_spelling_mistakes.get(bigram):
                words[i] = result
                del words[i + 1]

        if result := common_spelling_mistakes.get(word):
            words[i] = result

    return ' '.join(words)


def fix_typo(word):
    if not is_real(word):
        if len(word) > 1:
            if word[0] == word[1] and is_real(word[1:]):
                return word[1:]

            if word[-1] == word[-2] and is_real(word[:-1]):
                return word[:-1]

        for i, letter in enumerate(word):
            if c := letter_mix_map.get(letter):

                maybe = word[:i] + c + word[i+1:]

                if is_real(maybe):
                    return maybe

            if len(word) > 1:
                if c := letter_mix_map.get(word[i - 1] + letter):
                    maybe = word[:i - 1] + c + word[i + 1:]

                    if is_real(maybe):
                        return maybe

    return word


def explain_none(changes, i, change, explain):
    changes[i]['type'] = 'replace'
    changes[i]['change'] = changes[i]['origin']
    changes[i]['origin'] = change
    changes[i]['explain'] = explain


def bake_spelling():
    def fix(text):
        """
        Fixes incorrect spelling and grammatically incorrect sequences.

        Params:
            - text: The text to be fixed.

        Returns:
            - result: The fixed text.
            - changes: An incremental changelog of what and how.
        """

        # What has been changed and how?
        changes = []

        # TODO: Cache things.
        text = text.replace(',', '').replace('.', '').replace(' - ', ' ')

        words = list(map(fix_typo, text.split(' ')))
        unks = []
        words = []
        change_cache = {}

        for i, word in enumerate(text.split(' ')):
            fixed = fix_typo(word)
            words.append(fixed)

            if fixed != word:
                change_cache[i] = (word, 'Dette var nok en tastefejl.')

        sentence = ' '.join(words)
        sentence = low_hanging_fruits(sentence)

        computed, changes = prob_spell(sentence)

        masks = {}

        for i, word in enumerate(words):
            if word not in corpus_words:
                unks.append(word)
                words[i] = word

                # We need a somewhat fixed version for the language model to suggest.

                mask = computed.copy()[0].term.split()

                old = mask[i]
                mask[i] = '[MASK]'
                masks[i] = (word, mask, old)

        for i, change in change_cache.items():
            # This will always be none. The word was fixed before. :)
            old = changes[i]

            # The following will transform none-object into corresponding chonge.
            # Note: the origin will have been the change made befor correction pass.
            explain_none(changes, i, change[0], change[1])

        computed_text = computed[0].term

        result = []

        # Yea, I know. Nvm, what did I know??
        for i, word in enumerate(computed_text.split(' ')):
            if mask := masks.get(i):
                tokens = [x['token_str'] for x in unmasker(' '.join(mask[1]))]

                found_match = False

                for token in tokens:
                    if mask[0] in token or token in mask[0] and mask[2] not in corpus_words:

                        if changes[i]['type'] == 'none':
                            explain_none(changes, i, change[0], change[1])
                        else:
                            changes[i]['change'] = token
                            changes[i]['explain'] = 'Indsættelse af korrekt ord.'

                        result.append(token)
                        found_match = True
                        break

                if not found_match:
                    result.append(word)

            else:
                result.append(word)

        return ' '.join(result), changes

    return fix


if __name__ == "__main__":
    while True:
        text = input('> ')
        fix = bake_spelling()

        if text == '@open':
            with open('test_en.txt', 'r') as f, open('out.txt', 'w+') as out:
                for line in f:
                    out.write(f'{fix(line)}\n')

        print(fix(text))
