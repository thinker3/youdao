#coding=utf8

import os
from datetime import datetime
#from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from splinter import Browser


class Fetcher(object):
    def __init__(self):
        self.browser = None

    def quit(self):
        if self.browser:
            self.browser.quit()

    def get_html_by_phantomjs(self, url):
        self.browser.visit(url)
        html = self.browser.html  # <type 'unicode'>
        html = html.encode('utf-8')
        return html

    def get_html_by_urllib2(self, url):
        import urllib2
        html = urllib2.urlopen(url).read()
        return html

    def get_html_by_urlgrabber(self, url):
        import urlgrabber
        html = urlgrabber.urlopen(url).read()
        return html

    def get_html_by_wget(self, url):
        #import subprocess
        #subprocess.call(["wget", "-r", "-np", "-A", "files", url])
        # q, quiet; big O, output-document
        cmd = 'wget -q -O tempword.html %s' % url
        cmd = cmd.replace('&', '\&')
        os.system(cmd)
        f = open('tempword.html', 'r')
        html = f.read()
        f.close()
        os.remove('tempword.html')
        return html

    def get_html_by_requests(self, url):
        import requests
        html = requests.get(url).text
        return html

    def get_html(self, url):
        return self.get_html_by_requests(url)  # 1
        #return self.get_html_by_urlgrabber(url)  # 2
        #return self.get_html_by_wget(url)  # 2
        if self.which_getter == 'phantomjs':
            try:
                self.browser = Browser('phantomjs')  # 3
                return self.get_html_by_phantomjs(url)
            except:
                return self.get_html_by_urllib2(url)  # 2
        else:
            return self.get_html_by_urllib2(url)

    def query(self, word):
        url = "http://dict.youdao.com/search?tab=chn&keyfrom=dict.top&q="
        url += word
        before_fetching = datetime.now()
        html = self.get_html(url)
        after_fetching = datetime.now()
        time_fetching = after_fetching - before_fetching
        print 'time_fetching %f' % time_fetching.total_seconds()
        hxs = Selector(text=html)
        time_parsing = datetime.now() - after_fetching
        print 'time_parsing %f' % time_parsing.total_seconds()

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
            return possible, False
        item_dict = {}
        item_dict['name'] = word
        item_dict['phonetic'] = phonetic
        item_dict['meaning'] = meaning
        item_dict['example'] = example
        return item_dict, True

query_web = Fetcher()
