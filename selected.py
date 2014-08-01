#!/usr/bin/env python
# encoding: utf-8

import os
import sys

temp = list(sys.stdin)
word_path = os.path.expanduser('~/selected_word.txt')
if len(temp) >= 1:
    word = temp[0]
    f = open(word_path, 'w+')
    f.write(word)
    f.close()
