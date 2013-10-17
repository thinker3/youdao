#coding=utf8

import os
from datetime import datetime
from models import XmlItem
from lxml import etree
from scrapy.selector import XmlXPathSelector

def abspath(filename):
    dirname = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dirname, filename)

def init_list(filename='wordbook.myxml'):
    filename = abspath(filename)
    temp = []
    try:
        f = open(filename, 'r')
        xml = f.read()
    except:
        xml = ''
    finally:
        try:
            f.close()
        except:
            pass
    if not xml:
        return temp
    xxs =XmlXPathSelector(text=xml)
    items = xxs.select('//wordbook/item')
    for item in items:
        name = item.select('./name/text()').extract()[0]
        one = XmlItem(name)
        create_time = item.select('./create_time/text()').extract()[0]
        create_time= datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
        access_time = item.select('./access_time/text()').extract()[0]
        access_time = datetime.strptime(access_time, '%Y-%m-%d %H:%M:%S')
        score = item.select('./score/text()').extract()[0]
        score = int(score)
        setattr(one, 'create_time', create_time)
        setattr(one, 'access_time', access_time)
        setattr(one, 'score', score)
        temp.append(one)
    return temp

def save_list(items, filename='wordbook.myxml'):
    filename = abspath(filename)
    wordbook = etree.Element('wordbook')
    for one in items:
        item = etree.Element('item')
        if 1:
            name = etree.Element('name')
            name.text = one.name
            score = etree.Element('score')
            score.text = str(one.score)
            create_time = etree.Element('create_time')
            create_time.text = one.create_time.strftime('%Y-%m-%d %H:%M:%S')
            access_time = etree.Element('access_time')
            access_time.text = one.access_time.strftime('%Y-%m-%d %H:%M:%S')
            if 1:
                item.append(name)
                item.append(score)
                item.append(create_time)
                item.append(access_time)
        wordbook.append(item)
    s = etree.tostring(wordbook, pretty_print=True, encoding='utf8') # encoding is important
    f = open(filename, 'w')
    f.write(s)
    f.close()

