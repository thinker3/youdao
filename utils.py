#coding=utf8

import os
from datetime import datetime
from lxml import etree
#from scrapy.selector import Selector
from lxml_selector import Selector

DB_FILE_NAME = 'webyoudao.db'
XML_FILE_NAME = 'wordbook.myxml'
# Dropbox
YOUDAO_SYNC_PATH = '~/nuts/youdao_db_xml/'  # endswith '/'
#YOUDAO_SYNC_PATH = ''
delta = 100
search_url = "http://dict.youdao.com/search?q="


def abspath():
    dirname = os.path.dirname(os.path.abspath(__file__))
    return (os.path.join(dirname, XML_FILE_NAME),
            os.path.join(dirname, DB_FILE_NAME))


def get_xml_db_path():
    if YOUDAO_SYNC_PATH:
        xml_in_sync = os.path.expanduser(
            YOUDAO_SYNC_PATH) + XML_FILE_NAME
        db_in_sync = os.path.expanduser(YOUDAO_SYNC_PATH) + DB_FILE_NAME
        if os.path.exists(xml_in_sync) and os.path.exists(db_in_sync):
            return xml_in_sync, db_in_sync
    return abspath()


xmlpath, dbpath = get_xml_db_path()


def init_list():
    from models import XmlItem
    temp = []
    try:
        f = open(xmlpath, 'r')
        xml = f.read()
    except Exception:
        xml = ''
    finally:
        try:
            f.close()
        except Exception:
            pass
    if not xml:
        return temp
    xxs = Selector(text=xml)
    items = xxs.xpath('//wordbook/item')
    for item in items:
        name = item.xpath('./name/text()').extract()[0]
        one = XmlItem(name)
        create_time = item.xpath('./create_time/text()').extract()[0]
        create_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
        access_time = item.xpath('./access_time/text()').extract()[0]
        access_time = datetime.strptime(access_time, '%Y-%m-%d %H:%M:%S')
        score = item.xpath('./score/text()').extract()[0]
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
    # encoding is important
    s = etree.tostring(wordbook, pretty_print=True, encoding='utf8')
    f = open(xmlpath, 'w')
    f.write(s.decode('utf8'))
    f.close()


class Status(object):
    running = True


def get_url(word):
    return search_url + word


if __name__ == '__main__':
    pass
