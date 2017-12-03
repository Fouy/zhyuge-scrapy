# -*- coding: utf-8 -*-
import scrapy

'''
飘花电影Spider
'''
class PiaohuaSpider(scrapy.Spider):
    name = 'piaohua'
    allowed_domains = ['www.piaohua.com']
    start_urls = ['http://www.piaohua.com/']

    def parse(self, response):
        pass
