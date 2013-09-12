#coding=utf8
import peewee
from datetime import datetime
class Item(peewee.Model):
    name = peewee.CharField(primary_key=True)
    phonetic = peewee.CharField()
    meaning = peewee.TextField()
    example = peewee.TextField()

    class Meta:
        database = peewee.SqliteDatabase('webyoudao.db', check_same_thread=False)

    def getattr(self, attr):
        return object.__getattribute__(self, attr)

    def setattr(self, attr, value):
        object.__setattr__(self, attr, value)

    def convert(self):
        return XmlItem(self.name)

Item.create_table(True)

class XmlItem(object):
    def __init__(self, name):
        self.name = name.strip()
        self.score = 0
        self.create_time = datetime.now()
        self.access_time = datetime.now()

    def update_access_time(self):
        self.access_time = datetime.now()

    def convert(self):
        return Item.get(name=self.name)








