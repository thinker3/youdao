#coding=utf8

import time
import queue
import urllib.request, urllib.error, urllib.parse  # noqa
import requests
import threading
from datetime import datetime
from lxml_selector import Selector
from utils import Status, get_url
from models import Word

# disable http_proxy in urllib
urllib.request.getproxies = lambda: {}


class Manager(object):
    def __init__(self):
        pass

    def fetch(self, word):
        Fetcher(word).start()


class Fetcher(threading.Thread):
    time_out = 10
    sleep_interval = 0.05

    def __init__(self, word_queue, product_queue):
        threading.Thread.__init__(self)
        self.word_queue = word_queue
        self.product_queue = product_queue

    def run(self):
        while Status.running:
            time.sleep(self.sleep_interval)
            if not self.word_queue.empty():
                self.word = self.word_queue.get()
                dict_possible = self.query()
                self.product_queue.put((self.word, dict_possible))

    def get_html(self, url):
        try:
            proxies = {
                #'http': '',  # ok
                'http': None,
            }
            # proxies={} or proxies=None not work
            return requests.get(url, timeout=self.time_out, proxies=proxies).text
            return urllib.request.urlopen(url, timeout=self.time_out).read()
        except Exception as e:
            print(type(e), e)
            return ''

    def query(self):
        before_fetching = datetime.now()
        html = self.get_html(get_url(self.word.value))
        if not html:
            return ''
        after_fetching = datetime.now()
        time_fetching = after_fetching - before_fetching
        print()
        print(self.word.value)
        print(datetime.strftime(before_fetching, '%Y/%m/%d %H:%M:%S'))
        try:
            print('time_fetching %.2f' % time_fetching.total_seconds())
        except Exception:
            print('time_fetching %.2f' % time_fetching.seconds)
        hxs = Selector(text=html)
        if self.word.lang == 'cn':
            return self.query_cn(hxs)
        else:
            return self.query_en(hxs)

    def query_cn(self, hxs):
        en = []
        ps = hxs.xpath('//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/p[@class="wordGroup"]')
        for p in ps:
            text = p.xpath('./span[@class="contentTitle"]/*[self::a or self::span]/text()').extract()
            if text:
                text = ' '.join(text).split(';')
                en.extend(list(map(str.strip, text)))
        return '\n'.join(en)

    def query_en(self, hxs):
        phonetics = hxs.xpath('//div[@id="phrsListTab"]/h2[1]/div[1]/span')
        phonetic = ''
        for ph in phonetics:
            ph = ph.xpath('./span/text()').extract()
            if len(ph) > 0:
                phonetic += ph[0]

        lis = hxs.xpath(
            '//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li')
        meaning = ''
        for li in lis:
            try:
                temp_meaning = li.xpath('./text()').extract()[0] + '\n'
            except Exception:
                temp_meaning = ''
            if self.word.value.capitalize() in temp_meaning and '人名' in temp_meaning:
                continue
            else:
                meaning += temp_meaning

        examples = hxs.xpath('//div[@id="bilingual"]/ul/li')
        example = ''
        for li in examples:
            example_en = li.xpath('./p[1]/span//text()').extract()
            example_cn = li.xpath('./p[2]/span//text()').extract()
            example += ''.join(example_en) + '\n'
            example += ''.join(example_cn) + '\n'

        if not meaning:
            print('wrong word ?')
            try:
                possible = hxs.xpath(
                    '//div[@class="error-typo"]/h4/text()'
                ).extract()[0].strip() + '\n'
                possible += hxs.xpath(
                    '//div[@class="error-typo"]//a/text()').extract()[0]
            except Exception:
                possible = ''
            return possible
        item_dict = {}
        item_dict['name'] = self.word.value
        item_dict['phonetic'] = phonetic.encode('utf8')
        item_dict['meaning'] = meaning.encode('utf8')
        item_dict['example'] = example.encode('utf8')
        return item_dict


if __name__ == '__main__':
    word_queue = queue.Queue()
    product_queue = queue.Queue()
    Fetcher(word_queue, product_queue).start()
    while True:
        try:
            word = input('q to quit, input the word: ').strip()
        except KeyboardInterrupt:
            print()
            word = 'q'
        if word.lower() == 'q':
            Status.running = False
            break
        word = Word(word)
        if word.is_valid:
            word_queue.put(word)
            while True:
                if not product_queue.empty():
                    word, dict_possible = product_queue.get()
                    if isinstance(dict_possible, dict):
                        for k, v in list(dict_possible.items()):
                            print(v)
                    else:
                        print('\n' + dict_possible + '\n')
                    break
