#coding=utf8
import peewee
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
