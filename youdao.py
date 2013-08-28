#coding=utf8

import re, urllib2
from scrapy.selector import HtmlXPathSelector
def query_web(word):
    url = "http://dict.youdao.com/search?tab=chn&keyfrom=dict.top&q=" + word
    html = urllib2.urlopen(url).read()
    hxs = HtmlXPathSelector(text = html)

    phonetics = hxs.select('//div[@id="phrsListTab"]/h2[1]/div[1]/span')
    phonetic = ''
    for ph in phonetics:
        ph = ph.select('./span/text()').extract()
        if len(ph) > 0:
            phonetic += ph[0]

    lis = hxs.select('//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li')
    meaning = ''
    for li in lis:
        meaning += li.select('./text()').extract()[0] + '\n'

    examples = hxs.select('//div[@id="bilingual"]/ul/li')
    example = ''
    for li in examples:
        spans = li.select('./p[1]/span')
        example_en = []
        for span in spans:
            one = span.select('./text()').extract()
            if len(one) == 0:
                one = span.select('./b/text()').extract()
            example_en.extend(one)
        example_cn = li.select('./p[2]/span/text()').extract()
        example += ''.join(example_en) + '\n'
        example += ''.join(example_cn) + '\n'

    if not meaning:
        print 'wrong word ?'
        return 
    item_dict = {}
    item_dict['name'] = word
    item_dict['phonetic'] = phonetic
    item_dict['meaning'] = meaning 
    item_dict['example'] = example 
    return item_dict






