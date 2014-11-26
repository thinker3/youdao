youdao_like
========

Press shortcut to look up selected word, add words to wordbook to recite.

I use it on Ubuntu, Mac, Windows.

Ugly and a little bit hard to make it work the first time.

Data synchronization
-------

I use [nutstore](https://jianguoyun.com/s/downloads) to synchronize db and xml files among platforms(previously dropbox).

There is a variable in utils.py, you can change it if you have different path, make sure it is available on all platforms.

    YOUDAO_SYNC_PATH = '~/nuts/youdao_db_xml/'  # endswith '/'

Installation:
-------

### Ubuntu

    sudo apt-get install python-dev xsel python-tk libxml2-dev libxslt1-dev
    sudo pip install -i http://pypi.douban.com/simple/ peewee requests lxml

run:

    python my_youdao.py &

shortcut: left ctrl + left shift

notes: GUI doesn't pop up if minimized.

### Mac

    sudo pip install -i http://pypi.douban.com/simple/ peewee requests lxml

Add a service(with shortcut ctrl+shift+y) using Automator to run my_youdao.py

Add a service(with shortcut ctrl+cmd+z) using Automator to run selected.py

### Windows

You have to install [AutoHotKey](http://www.autohotkey.com/), then run selected.ahk by double-clicking it.

You have to set two env variables, TCL_LIBRARY, TK_LIBRARY, such as:

    set "TCL_LIBRARY=C:\Python27\tcl\tcl8.5"
    set "TK_LIBRARY=C:\Python27\tcl\tk8.5"

Install third-party libraries:

    easy_install -i http://pypi.douban.com/simple/ peewee requests lxml

run:

    python my_youdao.py

shortcut: alt+z or win+z or shift+z, you can change it in selected.ahk

How I run it?
-------

I am customed to Windows console and terminals.

I have a repository called [linux_settings](https://github.com/thinker3/linux_settings), it evolves to have settings for all platforms.

On Windows: `qui<tab> yd`, to be clear: `quick_edit_mode.bat yd`.

On Ubuntu: `yd`, an alias.

Nothing special on Mac.
