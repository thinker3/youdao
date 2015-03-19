#!/usr/bin/env python
# encoding: utf-8

import wx
from utils import save_list, Status
from layout import SearchFrame,  ReciteFrame, FlashFrame

parent = None
Search = SearchFrame


class Mixin(object):
    def close_handler(self, e=None):
        save_list(self.words)
        self.Destroy()
        if Status.running:
            self.master.btn_recite_handler()

    def enter_handler(self, e=None):
        self.show_phonetic()
        self.item.update_access_time()
        name = self.entry_name.GetValue().strip()
        self.entry_name.Disable()  # get value before disabled
        if name == self.item.name:
            self.item.score += 1
            self.rearrange(1)
            msg = 'Right, good!'
            self.showinfo(msg)
        else:
            self.item.score -= 2
            self.rearrange(0)
            msg = "Sorry, wrong!\nThe answer is ( %s )!" % self.item.name
            self.showinfo(msg)
        self.run()


class Recite(Mixin, ReciteFrame):  # Mixin first, why?
    title = 'Reciting'
    size = (800, 300)

    def __init__(self, master):
        super(Recite, self).__init__(parent, self.title, self.size)
        # if parent is not None, when parent close, child close
        # but child.close_handler not executed
        self.prepare_and_run(master)

    def special_run(self):
        self.entry_name.Enable()
        self.entry_name.SetValue('')
        self.entry_name.SetFocus()  # need to set focus, except the first time
        self.area_meaning.SetValue(self.item.convert().meaning)
        self.area_meaning.Disable()


class Flash(Mixin, FlashFrame):
    title = 'Flashing'
    size = (800, 300)

    def __init__(self, master):
        super(Flash, self).__init__(parent, self.title, self.size)
        self.prepare_and_run(master)

    def update(self):
        self.show_phonetic()
        self.show_meaning()
        self.item.update_access_time()

    def yes(self, e=None):
        self.update()
        msg = 'Good!'
        self.showinfo(msg)
        self.item.score += 1
        self.rearrange(1)
        self.run()

    def no(self, e=None):
        self.update()
        msg = 'Sorry!'
        self.showinfo(msg)
        self.item.score -= 2
        self.rearrange(0)
        self.run()

    def show_meaning(self, e=None):
        self.area_meaning.SetValue(self.item.convert().meaning)
        self.btn_show_meaning.Disable()
        self.area_meaning.Disable()

    def special_run(self):
        self.area_meaning.SetValue('')
        self.btn_show_meaning.Enable()
        self.label_name.SetLabel(self.item.name)

    def bind(self):
        super(Flash, self).bind()
        self.btn_no.Bind(wx.EVT_BUTTON, self.no)
        self.btn_yes.Bind(wx.EVT_BUTTON, self.yes)
        self.btn_show_meaning.Bind(wx.EVT_BUTTON, self.show_meaning)
