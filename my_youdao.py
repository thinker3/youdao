# coding=utf8

import os
import re
import sys
import Queue
import threading
import time
import peewee
import Tkinter as tk

from youdao import fetcher
from models import Item, proxy_db
from recite import Recite, Flash
from utils import init_list, save_list, dbpath

if sys.platform == 'darwin':
    title = 'Press ctrl+cmd+z to search selected word'
elif sys.platform == 'linux2':
    from keylogger import fetch_keys
    title = 'Press left ctrl and left shift to search selected word'
else:
    title = 'Press win+z to search selected word'

dirname = os.path.dirname(os.path.abspath(__file__))
word_path = os.path.join(dirname, 'word.txt')
sleep_interval = 0.05  # 0.5 is not responsive on linux2


class GetWord(threading.Thread):
    p = re.compile(r'[^a-zA-Z]')
    previous = ''

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True  # needed

    def run(self):
        while 1:
            time.sleep(sleep_interval)
            if sys.platform == 'linux2':
                self.get_word()
            else:
                self.read_word()

    def get_word(self):
        changed, modifiers, keys = fetch_keys()
        if changed:
            if modifiers['left ctrl'] and modifiers['left shift']:
                word = os.popen('xsel').read().strip()
                if word:
                    self.check_put_word(word)

    def read_word(self):
        if os.path.exists(word_path):
            f = open(word_path, 'r')
            word = f.readline().strip()
            f.close()
            if sys.platform == 'win32':
                os.popen('del %s' % word_path)
            else:
                os.popen('rm %s' % word_path)
            if word:
                self.check_put_word(word)

    def check_put_word(self, word):
        word = self.p.split(word)
        if len(word) >= 1:
            word = word[0]
            if len(word) >= 3:
                if self.previous != word:
                    self.previous = word
                    self.queue.put(word)
                else:
                    print 'same word ?'
                    self.queue.put(word)


def  init_close(old_func):
    def new_func(*args, **kwargs):
        # the db file can't be accessed by others
        #db = peewee.SqliteDatabase(dbpath, check_same_thread=True)
        #db = peewee.SqliteDatabase(dbpath, check_same_thread=False)
        #db = peewee.SqliteDatabase(dbpath, threadlocals=False)
        # OK, together with this proxy
        db = peewee.SqliteDatabase(dbpath, threadlocals=True)
        proxy_db.initialize(db)
        r = old_func(*args, **kwargs)
        proxy_db.initialize(None)
        return r
    return new_func


class GUI(object):
    item = None

    def __init__(self, queue):
        self.queue = queue
        self.root = tk.Tk()
        self.root.title(title)
        self.root.protocol("WM_DELETE_WINDOW", self.close_handler)
        self.frame = tk.Frame(self.root)
        self.words = init_list()
        self.init_UI()
        self.frame.after(100, self.respond)

    def respond(self):
        if not self.queue.empty():
            word = self.queue.get()
            self.search_word(word)
        self.frame.after(100, self.respond)

    def center(self):
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.rootsize = tuple(
            int(_) for _ in self.root.geometry().split('+')[0].split('x'))
        x = w / 2 - self.rootsize[0] / 2
        y = h / 2 - self.rootsize[1] / 2
        self.root.geometry("%dx%d+%d+%d" % (self.rootsize + (x, y)))

    def init_UI(self):
        if sys.platform == 'linux2':
            self.root.iconify()  # don't do it on darwin
        elif sys.platform == 'win32':
            self.root.iconify()
        self.name_string = tk.StringVar()
        self.entry_name = tk.Entry(self.frame, textvariable=self.name_string)
        self.entry_name.focus()
        # '<Enter>' is fired when mouse entering the input box
        self.entry_name.bind('<Return>', self.enter_handler)
        # for the numeric pad enter key
        self.entry_name.bind('<KP_Enter>', self.enter_handler)

        self.btn_add = tk.Button(self.frame, text="Add",
                              command=self.add_to_xml, state=tk.DISABLED)

        self.btn_recite = tk.Button(
            self.frame, text="Recite", command=self.create_recite_window)
        if not self.words:
            self.btn_recite.config(state=tk.DISABLED)

        self.btn_flash = tk.Button(
            self.frame, text="Flash", command=self.create_flash_window)
        if not self.words:
            self.btn_flash.config(state=tk.DISABLED)

        self.label_phonetic = tk.Label(self.frame, text='')

        self.area_meaning = tk.Text(self.frame, height=5, width=90, wrap=tk.WORD)
        self.scroll_meaning = tk.Scrollbar(self.frame)
        self.scroll_meaning.config(command=self.area_meaning.yview)
        self.area_meaning.tag_config(tk.SEL, background='red')
        self.area_meaning.configure(yscrollcommand=self.scroll_meaning.set)

        self.area_example = tk.Text(
            self.frame, height=9, width=90, background='white', wrap=tk.WORD)
        self.scroll_example = tk.Scrollbar(self.frame)
        self.scroll_example.config(command=self.area_example.yview)
        self.area_example.tag_config(tk.SEL, foreground='red')
        self.area_example.configure(yscrollcommand=self.scroll_example.set)

        self.btn_save = tk.Button(
            self.frame, text="Save", command=self.save_after_edit)

        self.btn_sort = tk.Button(self.frame, text="Sort", command=self.sort)
        self.lay_out()

    def lay_out(self):
        column = 0
        row = 0
        self.entry_name.grid(row=row, column=column)
        row += 1
        self.label_phonetic.grid(row=row, column=column)
        row += 1
        self.area_meaning.grid(row=row, column=column)
        row += 1
        self.area_example.grid(row=row, column=column)
        row += 1
        self.btn_save.grid(row=row, column=column)

        column += 1
        row = 2
        self.scroll_meaning.grid(row=row, column=column, sticky=tk.N + tk.S)
        row += 1
        self.scroll_example.grid(row=row, column=column, sticky=tk.N + tk.S)

        column += 1
        row = 0
        self.btn_add.grid(row=row, column=column)
        row += 1
        self.btn_recite.grid(row=row, column=column)
        row += 1
        self.btn_flash.grid(row=row, column=column)
        row += 1
        self.btn_sort.grid(row=row, column=column)
        row += 1
        self.frame.pack(padx=5, pady=5)

    def sort(self):
        self.btn_sort.config(state=tk.DISABLED)
        self.words.sort(key=lambda x: x.score)
        save_list(self.words)
        time.sleep(1)
        self.btn_sort.config(state=tk.NORMAL)

    @init_close
    def save_after_edit(self):
        if self.item:
            self.item.meaning = self.area_meaning.get('1.0', tk.END)
            self.item.example = self.area_example.get('1.0', tk.END)
            self.item.save()

    def create_recite_window(self):
        self.app = Recite(self)
        self.btn_recite.config(state=tk.DISABLED)
        self.btn_flash.config(state=tk.DISABLED)

    def create_flash_window(self):
        self.app = Flash(self)
        self.btn_recite.config(state=tk.DISABLED)
        self.btn_flash.config(state=tk.DISABLED)

    def enter_handler(self, event):
        word = self.name_string.get().strip()
        self.search_word(word)

    def btn_recite_handler(self):
        if self.words:
            self.btn_recite.config(state=tk.NORMAL)
            self.btn_flash.config(state=tk.NORMAL)
        else:
            self.btn_recite.config(state=tk.DISABLED)
            self.btn_flash.config(state=tk.DISABLED)

    def highlight(self, name):
        start = 1.0
        pos = self.area_example.search(name, start, stopindex=tk.END)
        while pos:
            length = len(self.item.name)
            #row, col = pos.split('.')
            #end = int(col) + length
            #end = row + '.' + str(end)
            end = '%s + %dc' % (pos, length)
            self.area_example.tag_add('highlight', pos, end)
            start = end
            pos = self.area_example.search(
                name,
                start,
                stopindex=tk.END
            )
        self.area_example.tag_config(
            'highlight',
            foreground='red',
            background='white',
        )

    def show_in_gui(self):
        self.center()
        self.btn_save.config(state=tk.NORMAL)
        if not self.in_xml():
            self.btn_add.config(state=tk.NORMAL)
        self.name_string.set(self.item.name)
        self.label_phonetic.__setitem__('text', self.item.phonetic)

        self.area_meaning.delete('1.0', tk.END)
        self.area_meaning.insert(tk.INSERT, self.item.meaning)

        self.area_example.delete('1.0', tk.END)
        self.area_example.insert(tk.INSERT, self.item.example)
        self.highlight(self.item.name)
        self.highlight(self.item.name.title())

        if self.root.state() == 'iconic':
            # normal, iconic, withdrawn, icon, zoomed
            self.root.deiconify()
        if sys.platform == 'darwin':
            # how to write long string
            long_cmd = (
                """/usr/bin/osascript -e 'tell app "Finder" """
                """to set frontmost of process "Python" to true'"""
            )
            os.system(long_cmd)
            self.root.deiconify()  # always normal even if minimized
        if sys.platform == 'linux2':
            self.root.attributes('-topmost', 1)
            self.root.attributes('-topmost', 0)
        if sys.platform != 'darwin':
            # To force a widget to have the focus even if the application isn't currently active
            self.root.focus_force()  # focus(), not works
        self.entry_name.focus()
        self.entry_name.select_range(0, tk.END)  # TclError: bad entry index "1.0"
        self.entry_name.icursor(tk.END)

    def clear(self, word='', meaning=''):
        self.center()
        self.name_string.set(word)
        self.label_phonetic.__setitem__('text', 'No such word or web failure.')
        self.area_meaning.delete('1.0', tk.END)
        self.area_meaning.insert(tk.INSERT, meaning)
        self.area_example.delete('1.0', tk.END)

        self.btn_add.config(state=tk.DISABLED)
        self.btn_save.config(state=tk.DISABLED)

        self.root.deiconify()
        self.root.attributes('-topmost', 1)
        self.root.attributes('-topmost', 0)
        self.root.focus_force()

    def in_xml(self):
        # return self.item.name in [one.name for one in self.words]
        for one in self.words:
            if self.item.name == one.name:
                return True
        return False

    @init_close
    def add_to_xml(self):
        self.btn_add.config(state=tk.DISABLED)
        if self.in_xml():  # strange duplicate items
            return
        # if add a word that is not in db now to xml, save it to db.
        try:
            item = Item.get(name=self.item.name)
        except:
            item = None
        if not item:
            self.item.save(force_insert=True)  # only save() not save to db

        try:
            if self.words:
                self.words.insert(1, self.item.convert())
            else:
                self.words.insert(0, self.item.convert())
            save_list(self.words)
        except Exception as e:
            print e

    @init_close
    def query_db(self, word):
        try:
            item = Item.get(name=word)
        except:
            item = None
        self.item = item

    @init_close
    def save(self, item_dict):
        # if no example, do not save to db, but if added to xml, save it to db.
        if item_dict['example']:
            self.item = Item.create(**item_dict)
        else:
            self.item = Item(**item_dict)

    def search_word(self, word):
        word = word.lower()
        self.query_db(word)  # if word not in db, set self.item = None
        if not self.item:
            item_dict_or_str = ''
            success = False
            try:
                item_dict_or_str, success = fetcher.query(word)
            except Exception as e:
                print e
            if item_dict_or_str and success:
                self.save(item_dict_or_str)  # save and set self.item
        if self.item:
            self.show_in_gui()
        else:
            self.clear(word, item_dict_or_str)  # here it is a string

    def close_handler(self):
        self.root.iconify()
        save_list(self.words)
        self.root.quit()


if __name__ == '__main__':
    queue = Queue.Queue()
    GetWord(queue).start()
    GUI(queue).root.mainloop()
