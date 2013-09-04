#coding=utf8
import os, re, threading
from time import sleep
from youdao import query_web
from keylogger import fetch_keys
import peewee
from models import Item
from Tkinter import Tk, Label
from Tkinter import *

class GUI(threading.Thread):
    item = None
    previous = ''
    running = True
    sleep_interval = 0.05
    p = re.compile(r'[^a-zA-Z]')

    def __init__(self):
        threading.Thread.__init__(self)
        self.root = Tk()
        self.root.title("Press ctrl to search seleted word")
        self.root.protocol("WM_DELETE_WINDOW", self.close_handler)
        self.frame=Frame(self.root)
        self.start()
        self.init_UI()
        self.root.mainloop()

    def center(self):
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.rootsize = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
        x = w/2 - self.rootsize[0]/2
        y = h/2 - self.rootsize[1]/2
        self.root.geometry("%dx%d+%d+%d" % (self.rootsize + (x, y)))

    def init_UI(self):
        self.root.iconify()
        self.label_name = Label(self.frame, text='')
        self.label_name.grid(row=0)
        self.label_phonetic = Label(self.frame, text='')
        self.label_phonetic.grid(row=1)

        self.area_meaning =Text(self.frame,height=3,width=50,wrap=WORD)
        self.area_meaning.grid(row=2)
        scroll_meaning=Scrollbar(self.frame)
        scroll_meaning.grid(row=2, column=1, sticky=N+S)
        scroll_meaning.config(command=self.area_meaning.yview)
        self.area_meaning.tag_config('color', background='red', foreground='white') # , wrap='word'
        self.area_meaning.configure(yscrollcommand=scroll_meaning.set)

        self.area_example =Text(self.frame,height=7,width=50,background='white',wrap=WORD)
        self.area_example.grid(row=3)
        scroll_example=Scrollbar(self.frame)
        scroll_example.grid(row=3, column=1, sticky=N+S)
        scroll_example.config(command=self.area_example.yview)
        self.area_example.tag_config(SEL, foreground='red')
        self.area_example.configure(yscrollcommand=scroll_example.set)

        self.frame.pack(padx=5, pady=5)

    def show_in_gui(self):
        self.center()
        self.label_name.__setitem__('text', self.item.name)
        self.label_phonetic.__setitem__('text', self.item.phonetic)

        self.area_meaning.config(state=NORMAL)
        self.area_meaning.delete('1.0', END)
        self.area_meaning.insert(INSERT, self.item.meaning, 'color')
        self.area_meaning.config(state=DISABLED)

        self.area_example.config(state=NORMAL)
        self.area_example.delete('1.0', END)
        self.area_example.insert(INSERT, self.item.example)
        self.area_example.config(state=DISABLED)

        self.root.deiconify()
        self.root.attributes('-topmost', 1)
        self.root.attributes('-topmost', 0)
        self.root.focus_force()

    def run(self):
        while self.running:
            sleep(self.sleep_interval)
            changed, modifiers, keys = fetch_keys()
            if changed:
                self.respond(modifiers)

    def query_db(self, word):
        try:
            item = Item.get(name=word)
        except:
            item = None
        self.item = item

    def save(self, item_dict):
        if item_dict['example']:
            self.item = Item.create(**item_dict)
        else:
            self.item = Item(**item_dict)

    def search(self, word):
        word = word.lower()
        self.query_db(word)
        item_dict = None
        if not self.item:
            try:
                item_dict = query_web(word)
            except:
                print 'web failure'
            if item_dict:
                self.save(item_dict)
        if self.item:
            self.show_in_gui()

    def respond(self, modifiers):
        if modifiers['left ctrl'] or modifiers['right ctrl']:
            var = os.popen('xsel').read().strip()
            if var:
                var = self.p.split(var)
                if len(var) >= 1:
                    var = var[0]
                    if len(var) >= 3:
                        if self.previous != var:
                            self.previous = var
                            self.search(var)
                        else:
                            print 'same word ?'

    def close_handler(self):
        self.root.iconify()
        self.running = False
        self.root.quit()


if __name__ == '__main__':
    gui = GUI()
