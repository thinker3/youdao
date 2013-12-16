#coding=utf8

import os, re, urllib2, urlgrabber, requests
from datetime import datetime
from scrapy.selector import HtmlXPathSelector
from splinter import Browser
import subprocess

class Fetcher(object):
    def __init__(self):
        self.browser = None

    def quit(self):
        if self.browser:
            self.browser.quit()

    def get_html_by_phantomjs(self, url):
        self.browser.visit(url)
        html = self.browser.html # <type 'unicode'>
        html = html.encode('utf-8')
        return html

    def get_html_by_urllib2(self, url):
        html = urllib2.urlopen(url).read()
        return html

    def get_html_by_urlgrabber(self, url):
        html = urlgrabber.urlopen(url).read()
        return html

    def get_html_by_wget(self, url):
        #subprocess.call(["wget", "-r", "-np", "-A", "files", url])
        cmd = 'wget -q -O tempword.html %s' % url # q, quiet; big O, output-document
        cmd = cmd.replace('&', '\&')
        os.system(cmd)
        f = open('tempword.html', 'r')
        html = f.read()
        f.close()
        os.remove('tempword.html')
        return html

    def get_html_by_requests(self, url):
        html = requests.get(url).text
        return html

    def get_html(self, url):
        return self.get_html_by_requests(url) # 1
        #return self.get_html_by_urlgrabber(url) # 2
        #return self.get_html_by_wget(url) # 2
        if self.which_getter == 'phantomjs':
            try:
                self.browser = Browser('phantomjs') # 3
                return self.get_html_by_phantomjs(url)
            except:
                return self.get_html_by_urllib2(url) # 2
        else:
            return self.get_html_by_urllib2(url)

    def query(self, word):
        url = "http://dict.youdao.com/search?tab=chn&keyfrom=dict.top&q=" + word
        before_fetching = datetime.now()
        html = self.get_html(url)
        after_fetching = datetime.now()
        time_fetching = after_fetching - before_fetching
        print 'time_fetching %f' % time_fetching.total_seconds()
        hxs = HtmlXPathSelector(text=html)
        time_parsing = datetime.now() - after_fetching
        print 'time_parsing %f' % time_parsing.total_seconds()

        phonetics = hxs.select('//div[@id="phrsListTab"]/h2[1]/div[1]/span')
        phonetic = ''
        for ph in phonetics:
            ph = ph.select('./span/text()').extract()
            if len(ph) > 0:
                phonetic += ph[0]

        lis = hxs.select('//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li')
        meaning = ''
        for li in lis:
            try:
                temp_meaning = li.select('./text()').extract()[0] + '\n'
            except:
                temp_meaning = ''
            if word.capitalize() in temp_meaning and u'人名' in temp_meaning:
                continue
            else:
                meaning += temp_meaning

        examples = hxs.select('//div[@id="bilingual"]/ul/li')
        example = ''
        for li in examples:
            example_en = li.select('./p[1]/span//text()').extract()
            example_cn = li.select('./p[2]/span//text()').extract()
            example += ''.join(example_en) + '\n'
            example += ''.join(example_cn) + '\n'

        if not meaning:
            print 'wrong word ?'
            try:
                possible = hxs.select('//div[@class="error-typo"]/h4/text()').extract()[0].strip() + '\n'
                possible += hxs.select('//div[@class="error-typo"]//a/text()').extract()[0]
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






