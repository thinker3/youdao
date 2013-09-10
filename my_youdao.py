#coding=utf8
import os, re, threading
from time import sleep
from youdao import query_web
from keylogger import fetch_keys
import peewee
from models import Item
from utils import init_list, save_list
from Tkinter import Tk, Label, Toplevel, Frame
from Tkinter import *
import tkMessageBox
from tkMessageBox import *

class Recite(object):
    def __init__(self, master):
        self.master = master
        self.window = Toplevel(self.master.root)
        self.window.title('Reciting')
        self.frame = Frame(self.window)
        self.init_UI()
        self.words = self.master.words
        self.run()
        self.window.protocol("WM_DELETE_WINDOW", self.close_handler)

    def close_handler(self):
        self.window.destroy()
        self.master.btn_recite.config(state=NORMAL)

    def init_UI(self):
        self.name_string = StringVar()
        self.entry_name = Entry(self.frame, textvariable=self.name_string)
        self.entry_name.grid(row=0)
        self.entry_name.bind('<Return>', self.enter_handler)

        self.btn_del = Button(self.frame, text="Delete", command=self.delete)
        self.btn_del.grid(row=0, column=1)

        self.label_phonetic = Label(self.frame, text='')
        self.label_phonetic.grid(row=1)

        self.btn_show_phonetic = Button(self.frame, text="Show phonetic", command=self.show_phonetic)
        self.btn_show_phonetic.grid(row=1, column=1)

        self.area_meaning =Text(self.frame,height=3,width=50,wrap=WORD)
        self.area_meaning.grid(row=2)
        scroll_meaning=Scrollbar(self.frame)
        scroll_meaning.grid(row=2, column=1, sticky=N+S)
        scroll_meaning.config(command=self.area_meaning.yview)
        self.area_meaning.configure(yscrollcommand=scroll_meaning.set)

        self.frame.pack(padx=5, pady=5)

    def delete(self):
        self.words.pop(0)
        self.run()

    def enter_handler(self, event):
        name = self.name_string.get().strip()
        if name:
            self.item.update_access_time()
        if name == self.item.name:
            self.item.score += 1
            self.rearrange(1)
            showinfo('Result', "Right, good!", parent=self.frame)
        else:
            self.item.score -= 1
            self.rearrange(0)
            showinfo('Result', "Sorry, wrong!\nThe answer is ( %s )!" % self.item.name, parent=self.frame)
        self.run()

    def show_phonetic(self):
        self.label_phonetic.__setitem__('text', self.item.phonetic)
        self.btn_show_phonetic.config(state=DISABLED)

    def run(self):
        item = self.words[0]
        self.name_string.set('')
        self.entry_name.focus()
        self.btn_show_phonetic.config(state=NORMAL)
        self.area_meaning.delete('1.0', END)
        self.area_meaning.insert(INSERT, item.meaning)
        self.item = item

    def rearrange(self, right):
        self.words.pop(0)
        if len(self.words) < 7:
            self.words.append(self.item)
            return
        if right:
            index = None
            for i, one in enumerate(self.words):
                if one.score > self.item.score:
                    index = i
                    break
            if not index:
                self.words.append(self.item)
            elif index < 6:
                self.words.insert(4, self.item)
            else:
                self.words.insert(index, self.item)
        else:
            self.words.insert(4, self.item)


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
        self.words = init_list()
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
        self.name_string = StringVar()
        self.entry_name = Entry(self.frame, textvariable=self.name_string)
        self.entry_name.grid(row=0)
        self.entry_name.bind('<Return>', self.enter_handler)

        self.btn_add = Button(self.frame, text="Add", command=self.add_to_xml, state=DISABLED)
        self.btn_add.grid(row=0, column=1)

        self.btn_recite = Button(self.frame, text="Recite", command=self.create_recite_window)
        self.btn_recite.grid(row=1, column=1)
        if not self.words:
            self.btn_recite.config(state=DISABLED)

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

    def create_recite_window(self):
        self.app = Recite(self)
        self.btn_recite.config(state=DISABLED)
    
    def enter_handler(self, event):
        word = self.name_string.get().strip()
        self.search(word)

    def show_in_gui(self):
        self.center()
        if not self.in_xml():
            self.btn_add.config(state=NORMAL)
        self.name_string.set(self.item.name)
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

    def in_xml(self):
        #return self.item.name in [one.name for one in self.words]
        for one in self.words:
            if self.item.name == one.name:
                return True
        return False

    def add_to_xml(self):
        try:
            if self.words:
                self.words.insert(1, self.item.convert())
            else:
                self.words.insert(0, self.item.convert())
        except:
            pass
        self.btn_add.config(state=DISABLED)

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
        save_list(self.words)
        self.running = False
        self.root.quit()


if __name__ == '__main__':
    gui = GUI()
