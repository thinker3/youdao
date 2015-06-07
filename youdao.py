#coding=utf8

import time
import Queue
import urllib2
import requests
import threading
from datetime import datetime
#from scrapy.selector import Selector
from lxml_selector import Selector
from utils import Status

# disable http_proxy in urllib2
urllib2.getproxies = lambda: {}


class Fetcher(threading.Thread):
    time_out = 10
    sleep_interval = 0.05

    def __init__(self, middle_queue, product_queue):
        threading.Thread.__init__(self)
        self.middle_queue = middle_queue
        self.product_queue = product_queue

    def run(self):
        while Status.running:
            time.sleep(self.sleep_interval)
            if not self.middle_queue.empty():
                word = self.middle_queue.get()
                dict_possible = self.query(word)
                self.product_queue.put(dict_possible)

    def get_html(self, url):
        try:
            proxies = {
                #'http': '',  # ok
                'http': None,
            }
            # proxies={} or proxies=None not work
            return requests.get(url, timeout=self.time_out, proxies=proxies).text
            return urllib2.urlopen(url, timeout=self.time_out).read()
        except Exception as e:
            print type(e), e
            return ''

    def query(self, word):
        url = "http://dict.youdao.com/search?tab=chn&keyfrom=dict.top&q="
        url += word
        before_fetching = datetime.now()
        html = self.get_html(url)
        if not html:
            return ''
        after_fetching = datetime.now()
        time_fetching = after_fetching - before_fetching
        print
        print word
        print datetime.strftime(before_fetching, '%Y/%m/%d %H:%M:%S')
        try:
            print 'time_fetching %.2f' % time_fetching.total_seconds()
        except:
            print 'time_fetching %.2f' % time_fetching.seconds

        hxs = Selector(text=html)
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
            except:
                temp_meaning = ''
            if word.capitalize() in temp_meaning and u'人名' in temp_meaning:
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
            print 'wrong word ?'
            try:
                possible = hxs.xpath(
                    '//div[@class="error-typo"]/h4/text()'
                ).extract()[0].strip() + '\n'
                possible += hxs.xpath(
                    '//div[@class="error-typo"]//a/text()').extract()[0]
            except:
                possible = ''
            return possible
        item_dict = {}
        item_dict['name'] = word
        item_dict['phonetic'] = phonetic.encode('utf8')
        item_dict['meaning'] = meaning.encode('utf8')
        item_dict['example'] = example.encode('utf8')
        return item_dict


if __name__ == '__main__':
    middle_queue = Queue.Queue()
    product_queue = Queue.Queue()
    Fetcher(middle_queue, product_queue).start()
    while True:
        word = raw_input('q to quit, input the word: ').strip()
        if word.lower() == 'q':
            Status.running = False
            break
        if word:
            middle_queue.put(word)
            while True:
                if not product_queue.empty():
                    dict_possible = product_queue.get()
                    if isinstance(dict_possible, dict):
                        for k, v in dict_possible.items():
                            print v
                    else:
                        print dict_possible
                    break
