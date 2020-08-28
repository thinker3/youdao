#!/usr/bin/env python
# encoding: utf-8

import sys
import ctypes


quick_edit = 0x0040

win32 = ctypes.windll.kernel32
handle = win32.GetStdHandle(-10)  # 3 ?
mode = ctypes.c_int(0)
win32.GetConsoleMode(handle, ctypes.byref(mode))
old_mode = mode.value


def main():
    # disable or enable Windows console(cmd.exe) quick edit mode
    if 'on' in sys.argv:
        #new_mode = 231
        new_mode = old_mode | quick_edit
        win32.SetConsoleMode(handle, new_mode)
    elif 'off' in sys.argv:
        #new_mode = 167
        new_mode = old_mode & (~quick_edit)
        win32.SetConsoleMode(handle, new_mode)
    else:
        print('usage: python %s on(off)' % __file__)


if __name__ == '__main__':
    main()
