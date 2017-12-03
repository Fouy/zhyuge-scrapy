# -*- coding: utf-8 -*-
import scrapy

'''
比特大熊Spider
'''
class BtdxSpider(scrapy.Spider):
    name = 'btdx'
    allowed_domains = ['www.btdx8.com']
    start_urls = ['http://www.btdx8.com/']

    def parse(self, response):
        pass
