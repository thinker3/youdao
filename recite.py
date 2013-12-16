#coding=utf8
import random
from utils import save_list
from Tkinter import *
from tkMessageBox import showinfo

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
        save_list(self.words)
        self.window.destroy()
        self.master.btn_recite_handler()

    def init_UI(self):
        self.name_string = StringVar()
        self.entry_name = Entry(self.frame, textvariable=self.name_string)
        self.entry_name.grid(row=0, sticky=W)
        self.entry_name.bind('<Return>', self.enter_handler)
        self.entry_name.bind('<KP_Enter>', self.enter_handler) # for the numeric pad enter key, no effects on message box

        self.btn_del = Button(self.frame, text="Delete", command=self.delete)
        self.btn_del.grid(row=0, column=1)

        self.label_phonetic = Label(self.frame, text='')
        self.label_phonetic.grid(row=1, sticky=W)

        self.btn_show_phonetic = Button(self.frame, text="Show phonetic", command=self.show_phonetic)
        self.btn_show_phonetic.grid(row=1, column=1)

        self.area_meaning =Text(self.frame,height=5,width=80,wrap=WORD)
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
        self.show_phonetic()
        self.item.update_access_time()
        name = self.name_string.get().strip()
        if name == self.item.name:
            self.item.score += 1
            self.rearrange(1)
            showinfo('Result', "Right, good!", parent=self.frame)
        else:
            self.item.score -= 2
            self.rearrange(0)
            showinfo('Result', "Sorry, wrong!\nThe answer is ( %s )!" % self.item.name, parent=self.frame)
        self.run()

    def show_phonetic(self):
        self.label_phonetic.__setitem__('text', self.item.convert().phonetic)
        self.btn_show_phonetic.config(state=DISABLED)

    def run(self):
        if len(self.words) == 0:
            self.close_handler()
            return
        self.item = self.words[0]
        self.name_string.set('')
        self.entry_name.focus()
        self.label_phonetic.config(text='')
        self.btn_show_phonetic.config(state=NORMAL)
        self.area_meaning.delete('1.0', END)
        try:
            self.area_meaning.insert(INSERT, self.item.convert().meaning)
        except:
            self.words.pop(0)
            self.run()

    def rearrange(self, right):
        if self.item != self.words[0]: # to avoid multiple enter events
            return
        self.words.pop(0)
        if self.item.score >= 6: # remove the word
            return
        if len(self.words) < 7:
            self.words.append(self.item)
            return
        # length >= 7
        if right:
            index = None
            for i, one in enumerate(self.words):
                if one.score > self.item.score:
                    index = i
                    break
            # if not index: # when i==0, it may be not right
            if index is None:
                self.words.append(self.item)
            elif index < 6:
                self.words.insert(4, self.item)
            else:
                self.words.insert(index, self.item)
        else:
            self.words.insert(4, self.item)
        # length >= 8
        if 0 == random.randint(0, 1):
            self.choose()

    def choose(self):
        index = random.randint(len(self.words)/2, len(self.words)-1)
        choosed = self.words.pop(index)
        print 'choosing %s, length is %d, index is %d, score is %d' % (choosed.name, len(self.words), index, choosed.score)
        self.words.insert(0, choosed)









