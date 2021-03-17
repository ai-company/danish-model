dictionary = [
    'løbesko'
] # Yet to come.

def correct_simple(a, b):
    if a[-1] in ['s', 'e']:
        if (compound := a + b) in dictionary:
            return compound

if __name__ == "__main__":
    while True:
        text = input('> ').split(' ')
        a = text[0]
        b = text[1]
        print(correct_simple(a, b))