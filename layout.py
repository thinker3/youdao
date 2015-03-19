#!/usr/bin/env python
# coding=utf8

import wx
from frames import BaseFrame, SecondaryFrame

rows = 5
cols = 2
vgap = 20
hgap = 10


class SearchFrame(BaseFrame):
    def __init__(self, parent, title, size):
        super(SearchFrame, self).__init__(parent, title, size)
        self.Centre()
        self.Show()

    def init_elements(self):
        super(SearchFrame, self).init_elements()
        self.entry_name = wx.TextCtrl(self.panel)
        self.entry_name.SetFocus()
        self.label_phonetic = wx.StaticText(self.panel, label='')

        self.area_meaning = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        self.area_example = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)

        self.btn_lookup = wx.Button(self.panel, label="Lookup")
        self.btn_add = wx.Button(self.panel, label="Add")
        self.btn_add.Disable()

        self.btn_recite = wx.Button(self.panel, label="Recite")
        self.btn_recite.Disable()

        self.btn_flash = wx.Button(self.panel, label="Flash")
        self.btn_flash.Disable()

        self.btn_save = wx.Button(self.panel, label="Save")
        self.btn_sort = wx.Button(self.panel, label="Sort")

    def lay_out(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        grid = wx.FlexGridSizer(rows, cols, vgap, hgap)
        grid.AddMany([
            (self.entry_name), (self.btn_lookup),
            (self.label_phonetic), (self.btn_add),
            (self.area_meaning, 1, wx.EXPAND), (self.btn_recite),
            (self.area_example, 1, wx.EXPAND), (self.btn_flash),
            (self.btn_save), (self.btn_sort),
        ])
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableRow(2, 1)
        grid.AddGrowableRow(3, 1)
        hbox.Add(grid, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)
        #self.panel.SetSizerAndFit(hbox)

    def enter_handler(self, e=None):
        word = self.entry_name.GetValue()
        if word:
            self.highlight(word)

    def highlight(self, name):
        # todo
        print 'highlight'


class ReciteFrame(SecondaryFrame):

    def __init__(self, parent, title, size):
        super(ReciteFrame, self).__init__(parent, title, size)
        self.Show()

    def init_elements(self):
        super(ReciteFrame, self).init_elements()
        self.entry_name = wx.TextCtrl(self.panel)
        self.entry_name.SetFocus()
        self.label_phonetic = wx.StaticText(self.panel, label='')
        self.area_meaning = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)

        self.btn_del = wx.Button(self.panel, label="Delete")
        self.btn_show_phonetic = wx.Button(self.panel, label="Show phonetic")

    def lay_out(self):
        rows = 3
        cols = 2
        vgap = 30
        hgap = 10

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        grid = wx.FlexGridSizer(rows, cols, vgap, hgap)
        grid.AddMany([
            (self.entry_name), (self.btn_del),
            (self.label_phonetic), (self.btn_show_phonetic),
            (self.area_meaning, 1, wx.EXPAND)
        ])
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableRow(2, 1)
        hbox.Add(grid, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)


class FlashFrame(SecondaryFrame):
    def __init__(self, parent, title, size):
        super(FlashFrame, self).__init__(parent, title, size)
        self.Show()

    def init_elements(self):
        super(FlashFrame, self).init_elements()
        self.label_name = wx.StaticText(self.panel)
        self.label_phonetic = wx.StaticText(self.panel, label='')
        self.area_meaning = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)

        self.btn_del = wx.Button(self.panel, label="Delete")
        self.btn_show_phonetic = wx.Button(self.panel, label="Show phonetic")
        self.btn_show_meaning = wx.Button(self.panel, label="Show meaning")

        self.btn_yes = wx.Button(self.panel, label='Yes')
        self.btn_no = wx.Button(self.panel, label='No')

    def lay_out(self):
        rows = 3
        cols = 3
        vgap = 30
        hgap = 10

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        grid = wx.FlexGridSizer(rows, cols, vgap, hgap)
        grid.AddMany([
            (self.label_name), (self.btn_yes), (self.btn_del),
            (self.label_phonetic), (self.btn_no), (self.btn_show_phonetic),
            (self.area_meaning, 1, wx.EXPAND), (self.label_empty), (self.btn_show_meaning),
        ])
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableRow(2, 1)
        hbox.Add(grid, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)


def search_test():
    app = wx.App()
    title = 'SearchFrame Test'
    size = (800, 500)
    SearchFrame(None, title, size)
    app.MainLoop()


def recite_test():
    app = wx.App()
    title = 'ReciteFrame Test'
    size = (800, 300)
    ReciteFrame(None, title, size)
    app.MainLoop()


def flash_test():
    app = wx.App()
    title = 'FlashFrame Test'
    size = (800, 300)
    FlashFrame(None, title, size)
    app.MainLoop()


if __name__ == '__main__':
    search_test()
    #recite_test()
    #flash_test()
