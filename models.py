#coding=utf8

from datetime import datetime
import peewee

proxy_db = peewee.Proxy()


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


class Item(peewee.Model):
    name = peewee.CharField(primary_key=True)
    phonetic = peewee.CharField()
    meaning = peewee.TextField()
    example = peewee.TextField()

    class Meta:
        database = proxy_db

    def getattr(self, attr):
        return object.__getattribute__(self, attr)

    def setattr(self, attr, value):
        object.__setattr__(self, attr, value)

    def convert(self):
        return XmlItem(self.name)


if __name__ == '__main__':
    #Item.create_table()
    # create_table(True), fail silently if the table already exists
    Item.create_table(True)
