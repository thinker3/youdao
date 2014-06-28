#coding=utf8

from datetime import datetime
#from scrapy.selector import Selector
from lxml_selector import Selector


class Fetcher(object):

    def get_html_by_urllib2(self, url):
        import urllib2
        html = urllib2.urlopen(url).read()
        return html

    def get_html_by_requests(self, url):
        import requests
        html = requests.get(url).text
        return html

    def get_html(self, url):
        return self.get_html_by_requests(url)  # 1
        return self.get_html_by_urllib2(url)  # 2

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
        item_dict['phonetic'] = phonetic.encode('utf8')
        item_dict['meaning'] = meaning.encode('utf8')
        item_dict['example'] = example.encode('utf8')
        return item_dict, True

fetcher = Fetcher()


if __name__ == '__main__':
    while True:
        query = raw_input('q to quit, input the word: ')
        if query.lower() == 'q': break
        item_dict, true = fetcher.query(query)
        if true:
            for k, v in item_dict.items():
                print v
