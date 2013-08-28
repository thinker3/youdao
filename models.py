#coding=utf8
import peewee
class Item(peewee.Model):
    name = peewee.CharField(primary_key=True)
    phonetic = peewee.CharField()
    meaning = peewee.TextField()
    example = peewee.TextField()

    class Meta:
        database = peewee.SqliteDatabase('webyoudao.db')

