def correct_simple(a, b):
    if a[-1] in ['s', 'e']:
        if (compound := a + b) in dictionary:
            return compound


def merge_compound_words(tokens, changes):
    last_noun = False
    for token in tokens:
        if token.pos_ == 'NOUN':

            last_pos = token.pos_


if __name__ == "__main__":
    while True:
        text = input('> ').split(' ')
        a = text[0]
        b = text[1]
        print(correct_simple(a, b))
