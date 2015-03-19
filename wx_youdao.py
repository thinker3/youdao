#!/usr/bin/env python
# coding=utf8

import os
import re
import sys
import time
import Queue
import peewee
import wx

from youdao import Fetcher
from models import Item, init_close_db
from utils import init_list, save_list, Status, delta
from word_getter import WordGetter
from action import Search, Recite, Flash

if sys.platform == 'darwin':
    title = 'Press ctrl+cmd+z to search selected word'
elif sys.platform == 'linux2':
    title = 'Press left ctrl and left shift to search selected word'
else:
    title = 'Press win+z to search selected word'
    from quick_edit_mode import win32, handle, old_mode, quick_edit

size = (800, 500)
p = re.compile(r'\w{2,}')
same_word_hint = 'same word ?'


class GUI(Search):
    previous = ''
    item = None

    def __init__(self, material_queue, middle_queue, product_queue):
        super(GUI, self).__init__(None, title, size)
        self.material_queue = material_queue
        self.middle_queue = middle_queue
        self.product_queue = product_queue
        self.item_queue = Queue.Queue()
        self.Bind(wx.EVT_CLOSE, self.close_handler)
        self.words = init_list()
        self.bind()
        wx.CallLater(delta, self.respond)

    def check_search_word(self, word):
        word_list = p.findall(word)
        if word_list:
            word = word_list[0].lower()
            if self.previous != word:
                self.previous = word
            else:
                print same_word_hint
            self.search_word(word)

    def respond(self):
        if not self.material_queue.empty():
            word = self.material_queue.get()
            self.check_search_word(word)
        if not self.item_queue.empty():
            self.item = self.item_queue.get()
            self.show_in_gui()
        if not self.product_queue.empty():
            item_dict_or_str = self.product_queue.get()
            if isinstance(item_dict_or_str, dict):
                item = self.save_item(item_dict_or_str)
                self.item_queue.put(item.to_unicode())
            else:
                self.clear(item_dict_or_str)
        wx.CallLater(delta, self.respond)

    def center(self):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.ize = tuple(
            int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w / 2 - self.ize[0] / 2
        y = h / 2 - self.ize[1] / 2
        self.geometry("%dx%d+%d+%d" % (self.ize + (x, y)))

    def bind(self):
        self.entry_name.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.btn_save.Bind(wx.EVT_BUTTON, self.save_after_edit)
        self.btn_add.Bind(wx.EVT_BUTTON, self.add_to_xml)
        self.btn_recite.Bind(wx.EVT_BUTTON, self.create_recite_window)
        self.btn_flash.Bind(wx.EVT_BUTTON, self.create_flash_window)
        if self.words:
            self.btn_recite.Enable()
            self.btn_flash.Enable()

        self.btn_sort.Bind(wx.EVT_BUTTON, self.sort)

    def sort(self, e=None):
        self.words = init_list()
        self.btn_sort.Disable()
        self.words.sort(key=lambda x: x.score)
        save_list(self.words)
        time.sleep(1)
        self.btn_sort.Enable()

    @init_close_db
    def save_after_edit(self, e=None):
        if self.item:
            self.item.meaning = self.area_meaning.GetValue()
            self.item.example = self.area_example.GetValue()
            self.item.save()

    def create_recite_window(self, e=None):
        self.words = init_list()
        self.recite = Recite(self)
        self.btn_recite.Disable()
        self.btn_flash.Disable()

    def create_flash_window(self, e=None):
        self.words = init_list()
        self.flash = Flash(self)
        self.btn_recite.Disable()
        self.btn_flash.Disable()

    def OnKeyUp(self, e=None):
        code = e.GetKeyCode()
        if code == wx.WXK_RETURN:
            self.enter_handler(e)

    def enter_handler(self, e=None):
        word = self.entry_name.GetValue()
        if word:
            self.material_queue.put(word)
        self.focus_in_entry()

    def btn_recite_handler(self, e=None):
        if self.words:
            self.btn_recite.Enable()
            self.btn_flash.Enable()
        else:
            self.btn_recite.Disable()
            self.btn_flash.Disable()

    def show_in_gui(self):
        self.btn_save.Enable()
        if not self.in_xml():
            self.btn_add.Enable()
        else:
            self.btn_add.Disable()
        self.entry_name.SetValue(self.item.name)
        self.label_phonetic.SetLabel(self.item.phonetic)
        self.area_meaning.SetValue(self.item.meaning)
        self.area_example.SetValue(self.item.example)
        #self.highlight(self.item.name)
        #self.highlight(self.item.name.title())
        self.popup_and_focus()

    def popup_and_focus(self):
        #print self.IsIconized()
        self.Raise()
        self.focus_in_entry()

    def focus_in_entry(self):
        #self.entry_name.SetFocus()  # no need to set focus?
        #self.entry_name.SetSelection(0, -1)  # not works
        self.entry_name.SetSelection(-1, -1)
        #self.entry_name.SetInsertionPointEnd()

    def clear(self, meaning=''):
        self.entry_name.SetValue(self.previous)
        self.label_phonetic.SetLabel('No such word or web failure.')
        self.area_meaning.SetValue(meaning)
        self.area_example.SetValue('')
        self.btn_add.Disable()
        self.btn_save.Disable()
        self.popup_and_focus()

    def in_xml(self):
        # return self.item.name in [one.name for one in self.words]
        for one in self.words:
            if self.item.name == one.name:
                return True
        return False

    @init_close_db
    def add_to_xml(self, e=None):
        self.btn_add.Disable()
        self.words = init_list()
        if self.in_xml():  # strange duplicate items
            return
        # if add a word that is not in db now to xml, save it to db.
        try:
            temp = Item.get(name=self.item.name)
        except:
            temp = None
        if not temp:
            self.item.save(force_insert=True)  # only save() not save to db
        try:
            if self.words:
                self.words.insert(1, self.item.convert())
            else:
                self.words.insert(0, self.item.convert())
            save_list(self.words)
        except Exception as e:
            print e

    @init_close_db
    def query_db(self, word):
        try:
            return Item.get(name=word)
        except:
            return None

    @init_close_db
    def save_item(self, item_dict):
        # if no example, do not save to db, but if added to xml, save it to db.
        if item_dict['example']:
            try:
                item = Item.create(**item_dict)
            except peewee.IntegrityError as e:
                print type(e), e
                item = self.query_db(item_dict['name'])
        else:
            item = Item(**item_dict)
        return item

    def search_word(self, word):
        item = self.query_db(word)
        if item:
            self.item_queue.put(item)
        else:
            self.middle_queue.put(word)

    def close_handler(self, e=None):
        if sys.platform == 'win32':
            '''
            # enable Windows console(cmd.exe) quick edit mode
            new_mode = old_mode | quick_edit
            win32.SetConsoleMode(handle, new_mode)
            '''
            # respect individual preference
            win32.SetConsoleMode(handle, old_mode)
        Status.running = False
        self.Hide()
        self.Destroy()

if __name__ == '__main__':
    if sys.platform == 'win32':
        # disable Windows console(cmd.exe) quick edit mode
        new_mode = old_mode & (~quick_edit)
        win32.SetConsoleMode(handle, new_mode)
    material_queue = Queue.Queue()
    middle_queue = Queue.Queue()
    product_queue = Queue.Queue()
    WordGetter(material_queue).start()
    Fetcher(middle_queue, product_queue).start()
    app = wx.App()
    GUI(material_queue, middle_queue, product_queue)
    app.MainLoop()