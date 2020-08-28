#!/usr/bin/env python
# encoding: utf-8

import os
import time
import queue
import random
import threading

from utils import Status

home = os.path.expanduser('~')
filename = 'selected_word.txt'
# TypeError: cannot concatenate 'str' and 'list' objects
#word_path = os.path.join([home, filename])
word_path = os.path.join(home, filename)
sleep_interval = 0.05  # 0.5 is not responsive on linux2


class WordGetter(threading.Thread):
    def __init__(self, queue=None, is_test=False):
        threading.Thread.__init__(self)
        self.queue = queue
        self.is_test = is_test

    def run(self):
        while Status.running:
            time.sleep(sleep_interval)
            self.read_word()

    def read_word(self):
        if os.path.exists(word_path):
            f = open(word_path, 'r')
            word = f.readline().strip()
            f.close()
            try:
                os.remove(word_path)
            except Exception as e:
                print(type(e), e)
                time.sleep(0.2)
                self.read_word()
            else:
                if word:
                    self.put_or_print_or_quit(word)

    def put_or_print_or_quit(self, word):
        if word == 'q' and self.is_test:
            print('quit')
            Status.running = False
        elif self.queue:
            self.queue.put(word)
            if self.is_test:
                print(self.queue.get())
        else:
            print(word)


if __name__ == '__main__':
    #getter = WordGetter(is_test=True)
    getter = WordGetter(queue=queue.Queue(), is_test=True)
    getter.start()
    while Status.running:
        try:
            f = open(word_path, 'w')
            r = random.randint(1, 100)
            f.write('hello %s' % r)
            f.close()
            time.sleep(2)
        except KeyboardInterrupt:
            Status.running = False
