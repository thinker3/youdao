#!/usr/bin/env python
# encoding: utf-8


import urllib2
import requests
from lxml import etree
from lxml.html import tostring


class Selector(object):
    def __init__(self, url=None, html=None, text=None, tree=None):
        html = html or text
        if tree is not None:
            self.tree = tree
        elif html:
            self.html = html
            self.tree = etree.HTML(self.html)
        else:
            self.url = url
            self.get_html_by_requests()
            self.tree = etree.HTML(self.html)

    def get_html_by_urllib2(self):
        self.html = urllib2.urlopen(self.url).read()

    def get_html_by_requests(self):
        self.html = requests.get(self.url).text

    def xpath(self, path):
        elements = self.tree.xpath(path)
        rlist = [self.__class__(tree=element) for element in elements]
        return SelectorList(rlist)

    def extract(self):
        # TypeError: Type 'lxml.etree._ElementUnicodeResult' cannot be serialized.
        # TypeError: Type '_ElementStringResult' cannot be serialized.
        if isinstance(self.tree, etree._ElementStringResult):
            return self.tree
        if isinstance(self.tree, etree._ElementUnicodeResult):
            return self.tree
        if hasattr(self.tree, 'text'):
            return self.tree.text
        return tostring(self.tree)
    
    '''
    def __str__(self):
        pass
    '''


class SelectorList(list):

    '''
    def __getslice__(self, i, j):
        return self.__class__(list.__getslice__(self, i, j))

    def xpath(self, xpath):
        return self.__class__(flatten([x.xpath(xpath) for x in self]))
    '''

    def extract(self):
        return [x.extract() for x in self]
