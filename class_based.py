#coding=utf8
import os, re, threading
from time import sleep
from youdao import query_web
from keylogger import fetch_keys
import peewee
from models import Item
from Tkinter import Tk, Label

class Detector(threading.Thread):
    item = None
    previous = ''
    running = True
    sleep_interval = 0.05
    p = re.compile(r'[^a-zA-Z]')
    def __init__(self):
        super(Detector, self).__init__()

    def run(self):
        while self.running:
            sleep(self.sleep_interval)
            changed, modifiers, keys = fetch_keys()
            if changed:
                self.respond(modifiers)

    def detect(self, root, labels):
        self.root = root
        self.labels = labels
        self.start()

    def relax(self):
        self.running = False

    def query_db(self, word):
        try:
            item = Item.get(name=word)
        except:
            item = None
        self.item = item

    def save(self, item_dict):
        self.item = Item.create(**item_dict)

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

    def show_in_gui(self):
        for one in self.labels:
            self.labels[one].__setitem__('text', self.item.getattr(one))
            self.labels[one].pack()
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.root.after_idle(self.root.call, 'wm', 'attributes', '.', '-topmost', False)
        self.root.focus_force()

class GUI():
    def __init__(self, holmes):
        self.holmes = holmes
        self.root = Tk()
        self.root.title("Press ctrl to search seleted word")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry("550x250+%d+%d" % (screen_width/2-275, screen_height/2-125))
        self.root.protocol("WM_DELETE_WINDOW", self.close_handler)


    def close_handler(self):
        self.holmes.relax()
        self.root.quit()

    def init_labels(self):
        label_name = Label(self.root, text='')
        label_name.pack()
        label_phonetic = Label(self.root, text='')
        label_phonetic.pack()
        label_meaning = Label(self.root, text='')
        label_meaning.pack()
        label_example = Label(self.root, text='')
        label_example.pack()
        self.labels = {}
        self.labels['name'] = label_name
        self.labels['phonetic'] = label_phonetic
        self.labels['meaning'] = label_meaning
        self.labels['example'] = label_example

    def appear(self):
        self.init_labels()
        self.holmes.detect(self.root, self.labels)
        self.root.mainloop()


if __name__ == '__main__':
    holmes = Detector()
    gui = GUI(holmes)
    gui.appear()
