#coding=utf8

import os
from datetime import datetime
from models import XmlItem
from lxml import etree
from scrapy.selector import XmlXPathSelector

DB_FILE_NAME = 'webyoudao.db'
XML_FILE_NAME = 'wordbook.myxml'
DROPBOX_YOUDAO_PATH = '~/Dropbox/youdao_db_xml/' # endswith '/'

def abspath():
    dirname = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dirname, XML_FILE_NAME), os.path.join(dirname, DB_FILE_NAME)

def get_xml_db_path():
    if DROPBOX_YOUDAO_PATH:
        xml_in_dropbox = os.path.expanduser(DROPBOX_YOUDAO_PATH) + XML_FILE_NAME 
        db_in_dropbox = os.path.expanduser(DROPBOX_YOUDAO_PATH) + DB_FILE_NAME 
    if os.path.exists(xml_in_dropbox) and os.path.exists(db_in_dropbox):
        return xml_in_dropbox, db_in_dropbox
    else:
        return abspath()

xmlpath, dbpath = get_xml_db_path()

def init_list():
    temp = []
    try:
        f = open(xmlpath, 'r')
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

def save_list(items):
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
    f = open(xmlpath, 'w')
    f.write(s)
    f.close()

