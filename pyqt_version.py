#coding=utf8
import os, re, threading
from time import sleep
from youdao import query_web
from keylogger import fetch_keys
from models import Item
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QShortcut

class GUI(QtGui.QWidget, threading.Thread):
    item = None
    previous = ''
    running = True
    sleep_interval = 0.05
    p = re.compile(r'[^a-zA-Z]')

    def __init__(self):
        threading.Thread.__init__(self)
        QtGui.QWidget.__init__(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.start()
        self.initUI()

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def initUI(self):
        self.nameL = QtGui.QLabel('')
        self.phonetic = QtGui.QLabel('')
        self.meaning = QtGui.QTextEdit()
        self.example = QtGui.QTextEdit()
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.nameL, 1, 0)
        grid.addWidget(self.phonetic, 2, 0)
        grid.addWidget(self.meaning, 3, 0, 5, 1)
        grid.addWidget(self.example, 4, 0, 5, 1)
        self.setLayout(grid) 
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Press Ctrl to search selected word')    
        self.setToolTip('Minimize to avoid annoying')
        self.show()

    def show_in_gui(self):
        self.nameL.setText(self.item.name)
        self.phonetic.setText(self.item.phonetic)
        #self.meaning.setText(self.item.meaning)
        #self.example.setText(self.item.example)
        if self.windowState() != Qt.WindowMinimized:
            print 'here'
            #self.setWindowState(Qt.WindowActive)
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.activateWindow()


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
        if modifiers['left ctrl']:
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


def main():
    app = QtGui.QApplication([])
    gui = GUI()
    exit(app.exec_())


if __name__ == '__main__':
    main()
