#!/usr/bin/env python
# encoding: utf-8

import os
import sys

temp = list(sys.stdin)
filename = 'word.txt'
dirname = os.path.dirname(os.path.abspath(__file__))
abspath = os.path.join(dirname, filename)
if len(temp) == 1:
    word = temp[0]
    f = open(abspath, 'w+')
    f.write(word)
    f.close()
