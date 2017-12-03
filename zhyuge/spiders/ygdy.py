# -*- coding: utf-8 -*-
import scrapy

'''
阳光电影Spider
'''
class YgdySpider(scrapy.Spider):
    name = 'ygdy'
    allowed_domains = ['www.ygdy8.com']
    start_urls = ['http://www.ygdy8.com/']

    def parse(self, response):
        pass
