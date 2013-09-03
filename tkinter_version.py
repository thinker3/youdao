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
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry("550x250+%d+%d" % (screen_width/2-275, screen_height/2-125))
        self.root.protocol("WM_DELETE_WINDOW", self.close_handler)
        self.start()
        self.init_UI()
        self.root.mainloop()

    def init_UI(self):
        self.label_name = Label(self.root, text='')
        self.label_name.pack()
        self.label_phonetic = Label(self.root, text='')
        self.label_phonetic.pack()
        self.area_meaning = Label(self.root, text='')
        self.area_meaning.pack()


        self.frame=Frame(self.root)
        self.frame.pack()

        self.area_example =Text(self.frame,height=10,width=50,background='white')
        scroll=Scrollbar(self.frame)
        self.area_example.configure(yscrollcommand=scroll.set)
        self.area_example.pack(side=LEFT)
        scroll.pack(side=RIGHT,fill=Y)
        #self.frame.pack(side=TOP)

    def show_in_gui(self):
        self.label_name.__setitem__('text', self.item.name)
        self.label_name.pack()
        self.label_phonetic.__setitem__('text', self.item.phonetic)
        self.label_phonetic.pack()
        self.area_meaning.__setitem__('text', self.item.meaning)
        self.area_meaning.pack()

        self.area_example.insert(INSERT, '')
        self.area_example.insert(INSERT, self.item.example)

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
