#!/usr/bin/env python
# encoding: utf-8

import random
import wx
from utils import Status, delta

#not_resizable = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)  # ok
not_resizable = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)


class BaseFrame(wx.Frame):
    def __init__(self, parent, title, size):
        super(BaseFrame, self).__init__(parent, title=title, size=size, style=not_resizable)
        self.Bind(wx.EVT_CLOSE, self.close_handler)
        self.init_elements()
        if hasattr(self, 'entry_name'):
            self.entry_name.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.lay_out()

    def init_elements(self):
        self.panel = wx.Panel(self)
        self.label_empty = wx.StaticText(self.panel, label='')

    def lay_out(self):
        pass

    def OnKeyUp(self, e=None):
        code = e.GetKeyCode()
        if code == wx.WXK_RETURN:
            self.enter_handler(e)

    def enter_handler(self, e=None):
        pass

    def close_handler(self, e=None):
        self.Destroy()


class SecondaryFrame(BaseFrame):
    def __init__(self, parent, title, size):
        super(SecondaryFrame, self).__init__(parent, title, size)
        wx.CallLater(delta, self.check_running)

    def prepare_and_run(self, master):
        self.master = master
        self.words = self.master.words
        self.bind()
        self.run()

    def run(self):
        if len(self.words) == 0:
            self.close_handler()
            return
        self.item = self.words[0]
        if self.item.convert() is None:
            self.words.pop(0)
            return self.run()
        self.btn_show_phonetic.Enable()
        self.area_meaning.Enable()
        self.label_phonetic.SetLabel('')
        # press enter once, fires enter_handler twice, why?
        wx.CallLater(delta * 10, self.special_run)

    def showinfo(self, msg, style=None):
        #parent = self
        parent = None
        caption = 'Result'
        style = style or wx.OK | wx.ICON_INFORMATION
        dialog = wx.MessageDialog(parent, msg, caption, style)
        dialog.ShowModal()
        dialog.Destroy()  # needed?
        #wx.MessageBox(msg, caption, style)

    def show_phonetic(self, e=None):
        self.label_phonetic.SetLabel(self.item.convert().phonetic)
        self.btn_show_phonetic.Disable()

    def delete(self, e=None):
        self.words.pop(0)
        self.run()

    def bind(self):
        self.btn_del.Bind(wx.EVT_BUTTON, self.delete)
        self.btn_show_phonetic.Bind(wx.EVT_BUTTON, self.show_phonetic)

    def check_running(self):
        if not Status.running:
            self.close_handler()
        wx.CallLater(delta, self.check_running)

    @property
    def length(self):
        return len(self.words)

    def rearrange(self, right):
        if self.item != self.words[0]:  # to avoid multiple enter events
            return
        self.words.pop(0)
        if self.item.score >= 6:  # remove the word
            return
        if len(self.words) < 7:
            self.words.append(self.item)
            return
        # length >= 7
        if right:
            index = self.length - 1
            while index:
                if self.item.score >= self.words[index].score:
                    break
                else:
                    index -= 1
            index += 1
            if index < 6:
                self.words.insert(4, self.item)
            else:
                self.words.insert(index, self.item)
        else:
            self.words.insert(4, self.item)
        # length >= 8
        if 0 == random.randint(0, 1):
            self.choose()

    def choose(self):
        index = random.randint(len(self.words) / 2, len(self.words) - 1)
        choosed = self.words.pop(index)
        print('choosing %s, length is %d, index is %d, score is %d' % (
            choosed.name, len(self.words), index, choosed.score))
        self.words.insert(0, choosed)
