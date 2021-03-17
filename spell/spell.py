from transformers import pipeline
from prob_spell   import init
from nltk.corpus  import words as corpus_words

import nltk
import distance

nltk.download('words')

corpus_words = corpus_words.words()

unmasker = pipeline('fill-mask', model='distilbert-base-uncased')
prob_spell = init()

# TODO: Move to CSV :)
letter_mix_map = {
    'ie': 'ei',
    'ks': 'x',
    'k':  'ck',
    'mm': 'm',
    'm':  'mm',
    'tt': 't',
    't':  'tt',
    'l':  'll',
    'll': 'l',
    'u':  'ou',
    'ou': 'u',
    'oy': 'oi',
    'o':  'ou',
    'y':  'i',
    'i':  'y',
    'dd': 'd',
    'd':  'dd',
    'tc': 'tch',
}

common_spelling_mistakes = {
    'can not': 'cannot',
    'isnt': 'isn\'t',
    'cant': 'can\'t',
    'wont': 'won\'t',
    'arent': 'aren\'t',
}

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
                maybe = word[:i - 1] + c + word[i:]

                if is_real(maybe):
                    return maybe
            
            if len(word) > 1:
                if c := letter_mix_map.get(word[i - 1] + letter):
                    maybe = word[:i - 1] + c + word[i + 1:]

                    if is_real(maybe):
                        return maybe

    return word

def bake_spelling():
    def fix(text):
        unks = []

        words = list(map(fix_typo, text.split(' ')))

        masks = {}

        for i, word in enumerate(words):
            if word not in corpus_words:
                unks.append(word)
                words[i] = word

                mask = prob_spell(' '.join(text))[0].term.split(' ')
                old = mask[i]
                mask[i] = '[MASK]'
                masks[i] = (word, mask, old)

        result   = []
        sentence = ' '.join(words)
        sentence = low_hanging_fruits(sentence)

        computed_text = prob_spell(sentence)[0].term

        # Yea, I know.
        for i, word in enumerate(computed_text.split(' ')):
            if mask := masks.get(i):
                tokens = [x['token_str'] for x in unmasker(' '.join(mask[1]))]

                found_match = False

                for token in tokens:
                    if mask[0] in token or token in mask[0] and mask[2] not in corpus_words:
                        result.append(token)
                        found_match = True
                        break

                if not found_match:
                    result.append(word)

            else:
                result.append(word)

        return ' '.join(result)

    return fix

while True:
    text = input('> ')
    fix = bake_spelling()

    if text == '@open':
        with open('test_en.txt', 'r') as f, open('out.txt', 'w+') as out:
            for line in f:
                out.write(f'{fix(line)}\n')

    print(fix(text))