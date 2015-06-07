#!/usr/bin/env python
# encoding: utf-8

import wx
import time
import win32con
import win32com.client
import win32clipboard


class HotKey(object):
    def __init__(self, frame):
        self.frame = frame
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.regHotKey(1, win32con.MOD_ALT, 'z')
        self.regHotKey(2, win32con.MOD_WIN, 'z')
        self.regHotKey(3, win32con.MOD_SHIFT, 'z')

    def send_keys(self, keys):
        self.shell.SendKeys(keys)

    def send_ctrl_c(self):
        self.send_keys("^c")

    def regHotKey(self, hotKeyId, mod, key):
        self.frame.RegisterHotKey(
            hotKeyId,
            mod,
            ord(key.upper()),
            )
        self.frame.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=hotKeyId)

    def handleHotKey(self, evt):
        time.sleep(0.5)  # at least 0.3
        self.send_ctrl_c()
        time.sleep(0.1)
        text = self.get_clipboard_text()
        self.set_clipboard_text()
        if text:
            self.frame.material_queue.put(text)

    def get_clipboard_text(self):
        try:
            win32clipboard.OpenClipboard()
        except:
            return ''
        try:
            text = win32clipboard.GetClipboardData()
        except TypeError as e:
            print e
            text = ''
        finally:
            win32clipboard.CloseClipboard()
        return text

    def set_clipboard_text(self, text=''):
        try:
            win32clipboard.OpenClipboard()
        except:
            return
        try:
            win32clipboard.SetClipboardText(text)
        except TypeError as e:
            print e
        finally:
            win32clipboard.CloseClipboard()
