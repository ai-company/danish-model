from os.path import join, dirname

import sys
import random

import tqdm

if __name__ == '__main__':
    if len(sys.argv) == 3:
        with open(sys.argv[1], 'r') as f:
            lines = f.readlines()
            random.shuffle(lines)

        with open(sys.argv[2], 'w+') as f:
            for line in tqdm.tqdm(lines):
                f.write(line)
    else:
        print('Dumt.')
