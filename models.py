#coding=utf8
import peewee
from datetime import datetime
class Item(peewee.Model):
    name = peewee.CharField(primary_key=True)
    phonetic = peewee.CharField()
    meaning = peewee.TextField()
    example = peewee.TextField()

    class Meta:
        database = peewee.SqliteDatabase('webyoudao.db')

    def getattr(self, attr):
        return object.__getattribute__(self, attr)

    def setattr(self, attr, value):
        object.__setattr__(self, attr, value)

    def convert(self):
        return XmlItem(self.name, self.meaning, self.phonetic, self.example)

class XmlItem(object):
    def __init__(self, name, meaning, phonetic='', example='', score=0, create_time=None, access_time=None):
        self.name = name.strip()
        self.meaning = meaning.strip()
        self.phonetic = phonetic.strip()
        self.example = example.strip()
        self.score = score
        self.create_time = create_time if create_time else datetime.now()
        self.access_time = access_time if access_time else datetime.now()

    def update_access_time(self):
        self.access_time = datetime.now()








