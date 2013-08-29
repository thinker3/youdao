import os, re
from time import sleep
from youdao import query_web
from keylogger import fetch_keys
import peewee
from models import Item
from Tkinter import Tk, Label

p = re.compile(r'[^a-zA-Z]')
last = ''

def log(callback, sleep_interval=.05):
    while 1:
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

def show(item):
    print item.name
    print item.phonetic
    print item.meaning
    print item.example


def App(root):
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

def show_in_gui(item):
    global labels
    for one in labels:
        labels[one].__setitem__('text', item.getattr(one))
        labels[one].pack()


#if __name__ == '__main__':
root = Tk()
labels = App(root)
root.mainloop()
log(ctrl_pressed)
