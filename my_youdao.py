#!/usr/bin/env python
# coding=utf8

import os
import time
import queue
import subprocess

import wx
import peewee

from youdao import Fetcher
from models import Word, Item, init_close_db
from utils import init_list, save_list, Status, delta, get_url
from word_getter import WordGetter
from action import Search, Recite, Flash

size = (800, 500)
same_word_hint = 'same word ?'
title = 'Press ctrl+cmd+z to search selected word'


class GUI(Search):
    previous = ''
    item = None

    def __init__(self, material_queue, word_queue, product_queue):
        super(GUI, self).__init__(None, title, size)
        self.material_queue = material_queue
        self.word_queue = word_queue
        self.product_queue = product_queue
        self.item_queue = queue.Queue()
        self.Bind(wx.EVT_CLOSE, self.close_handler)
        self.words = init_list()
        self.bind()
        wx.CallLater(delta, self.respond)

    def check_search_word(self, word):
        word = Word(word)
        if word.is_valid:
            if self.previous != word.value:
                self.previous = word.value
            else:
                print(same_word_hint)
            self.search_word(word)
        else:
            self.clear(word, 'Invalid word.')

    def respond(self):
        if not self.material_queue.empty():
            word = self.material_queue.get()
            self.check_search_word(word)
        if not self.item_queue.empty():
            self.item = self.item_queue.get()
            self.show_in_gui()
        if not self.product_queue.empty():
            word, item_dict_or_str = self.product_queue.get()
            if isinstance(item_dict_or_str, dict):
                # if no example, do not save to db, but if added to xml, save it to db.
                if item_dict_or_str['example']:
                    item = self.save_item(item_dict_or_str)
                else:
                    item = Item(**item_dict_or_str)
                self.item_queue.put(item)
            else:
                self.clear(word, item_dict_or_str)
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
        self.btn_lookup.Bind(wx.EVT_BUTTON, self.enter_handler)
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
    def save_after_edit(self, event=None):
        if self.item:
            self.item.meaning = self.area_meaning.GetValue()
            self.item.example = self.area_example.GetValue()
            try:
                self.item.save(force_insert=True)
            except peewee.IntegrityError as e:
                print(type(e), e)
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
        self.mac_raise(subproc=True)
        self.focus_in_entry()

    def mac_raise(self, subproc=False):
        #nsapp = NSRunningApplication.runningApplicationWithProcessIdentifier_(os.getpid())
        #nsapp.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
        if self.IsIconized():
            self.Iconize(False)
        if subproc:
            subprocess.Popen([
                'osascript',
                '-e',
                '''
                tell application "System Events"
                set procName to name of first process whose unix id is %s
                end tell
                tell application procName to activate
                ''' % os.getpid(),
            ])
        else:
            long_cmd = (
                """/usr/bin/osascript -e 'tell app "Finder" """
                """to set frontmost of process "Python" to true'"""
            )
            os.system(long_cmd)
        #self.Raise()  # shake; tremble; vibrate, not needed

    def focus_in_entry(self):
        self.entry_name.SetFocus()  # no need to set focus? need
        #self.entry_name.SetSelection(0, -1)  # not works
        self.entry_name.SetSelection(-1, -1)
        #self.entry_name.SetInsertionPointEnd()

    def clear(self, word, meaning):
        meaning = meaning or 'No such word or web failure.'
        self.entry_name.SetValue(word.value)
        self.label_phonetic.SetLabel('')
        self.area_meaning.SetValue(meaning)
        self.area_example.SetValue(get_url(word.value))
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
    def add_to_xml(self, event=None):
        self.btn_add.Disable()
        self.words = init_list()
        if self.in_xml():  # strange duplicate items
            return
        # if add a word that is not in db now to xml, save it to db.
        try:
            temp = Item.get(name=self.item.name)
        except Exception:
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
            print(e)

    @init_close_db
    def query_db(self, word):
        try:
            return Item.get(name=word)
        except Exception:
            return None

    @init_close_db
    def save_item(self, item_dict):
        try:
            item = Item.create(**item_dict)
            item = item.to_unicode()
        except peewee.IntegrityError as e:
            print(type(e), e)
            item = self.query_db(item_dict['name'])
        return item

    def search_word(self, word):
        if word.lang == 'cn':
            self.word_queue.put(word)
        else:
            item = self.query_db(word.value)
            if item:
                self.item_queue.put(item)
            else:
                self.word_queue.put(word)

    def close_handler(self, e=None):
        Status.running = False
        self.Hide()
        self.Destroy()


if __name__ == '__main__':
    material_queue = queue.Queue()
    word_queue = queue.Queue()
    product_queue = queue.Queue()
    WordGetter(material_queue).start()
    Fetcher(word_queue, product_queue).start()
    app = wx.App()
    GUI(material_queue, word_queue, product_queue)
    app.MainLoop()
