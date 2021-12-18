#!/usr/bin/env python3

import sys

from grammar.grammar import play

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide playground argument.')
        sys.exit(1)

    playground = sys.argv[1]

    {
        'grammar': play()
    }.get(playground, lambda: print('Invalid playground.'))
