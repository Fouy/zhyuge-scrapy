# -*- coding: utf-8 -*-
import scrapy

'''
迅雷仓Spider
'''
class XunleicangSpider(scrapy.Spider):
    name = 'xunleicang'
    allowed_domains = ['www.xunleicang.com']
    start_urls = ['http://www.xunleicang.com/']

    def parse(self, response):
        pass
