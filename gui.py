#coding=utf8
import os, re, threading
from time import sleep
from youdao import query_web
from keylogger import fetch_keys
import peewee
from models import Item
from Tkinter import Tk, Label

last = ''
running = True
p = re.compile(r'[^a-zA-Z]')

def log(callback, sleep_interval=.05):
    while running:
        sleep(sleep_interval)
        changed, modifiers, keys = fetch_keys()
        if changed:
            callback(modifiers, search)

def ctrl_pressed(modifiers, callback):
    global last
    if modifiers['left ctrl'] or modifiers['right ctrl']:
        var = os.popen('xsel').read().strip()
        if var:
            var = p.split(var)
            if len(var) >= 1:
                var = var[0]
                if len(var) >= 3:
                    if last != var:
                        last = var
                        callback(var)
                    else:
                        print 'same word ?'

def query_db(word):
    try:
        item = Item.get(name=word)
    except:
        item = None
    return item

def search(word):
    word = word.lower()
    item = query_db(word)
    item_dict = None
    if not item:
        try:
            item_dict = query_web(word)
        except:
            print 'web failure'
        if item_dict:
            item = save(item_dict)
    if item:
        show_in_gui(item)

def save(item_dict):
    item = Item.create(**item_dict)
    return item

class App(threading.Thread):
    def __init__(self, log, callback):
        super(App, self).__init__()
        self.callback = callback
        self.log = log

    def run(self):
        self.log(self.callback)

def get_lables(root):
    label_name = Label(root, text='')
    label_name.pack()

    label_phonetic = Label(root, text='')
    label_phonetic.pack()

    label_meaning = Label(root, text='')
    label_meaning.pack()

    label_example = Label(root, text='')
    label_example.pack()
    labels = {}
    labels['name'] = label_name
    labels['phonetic'] = label_phonetic
    labels['meaning'] = label_meaning
    labels['example'] = label_example
    return labels

def handler():
    global running, root
    root.quit()
    running = False

def show_in_gui(item):
    global labels, root
    for one in labels:
        labels[one].__setitem__('text', item.getattr(one))
        labels[one].pack()
    root.call('wm', 'attributes', '.', '-topmost', True)
    root.after_idle(root.call, 'wm', 'attributes', '.', '-topmost', False)
    root.focus_force() # works


#if __name__ == '__main__':
root = Tk()
labels = get_lables(root)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry("550x250+%d+%d" % (screen_width/2-275, screen_height/2-125))
root.protocol("WM_DELETE_WINDOW", handler)
try:
    app = App(log, ctrl_pressed)
    app.start()
    root.mainloop()
except: # not work
    running = False
    root.quit()
