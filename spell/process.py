from os.path import join, dirname

import sys
import spacy

if __name__ == '__main__':
    nlp = spacy.load('da_core_news_lg')

    if len(sys.argv) < 2:
        print('Please provide: <corpus> <language code>')
        print('... will automatically generate bigrams_<code>.txt and dictionary_<code>.txt')
        
        sys.exit(1)
    else:
        dictionary_path = join(dirname(__file__), f'dictionary_{sys.argv[2]}.txt')
        bigrams_path = join(dirname(__file__), f'bigrams_{sys.argv[2]}.txt')

        print(bigrams_path, dictionary_path)

        bigrams = {}
        dictionary = {}

        with open(join(dirname(__file__), 'wordbook.tx')) as f:
            wordbook = f.readlines()

        with open(sys.argv[1], 'r') as input_f:
            for line in input_f:
                words = line.split(' ')

                for i, word in enumerate(words[:-2]):
                    if word in wordbook:
                        if words[i + 1] in wordbook:
                            bigram = f'{word} {words[i + 1]}'

                            if bigram not in bigrams:
                                bigrams[bigram] = 0

                            if word not in dictionary:
                                dictionary[word] = 0

                            bigrams[bigram]  += 1

                        dictionary[word] += 1

        with open(dictionary_path, 'w') as dict_f,\
             open(bigrams_path, 'w') as bigrams_f:

            dict_f.write('\n'.join([f'{w} {i}' for w, i in dictionary.items()]))
            bigrams_f.write('\n'.join([f'{w} {i}' for w, i in bigrams.items()]))
