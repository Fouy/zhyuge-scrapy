# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request

from zhyuge.items import PictureItem, PictureUrlItem

'''
妹子图Spider （图片分类归属，全部归属"性感美女"）
'''
class MzituSpider(scrapy.Spider):
    name = 'mzitu'
    allowed_domains = ['www.mzitu.com']
    start_urls = ['http://www.mzitu.com/']

    # mzitu图片基地址
    base_url = 'http://www.mzitu.com'
    '''
    起始URL：参数顺序依次为：
        分类：xinggan 性感妹子、japan 日本妹子、taiwan 台湾妹子、mm 清纯妹子
    '''
    first_url = 'http://www.mzitu.com/{type}/page/{pageNo}/'
    typeList = ['xinggan', 'japan', 'taiwan', 'mm']

    '''
    开始请求列表
    '''

    def start_requests(self):
        # 抓取图片数据（初始化抓取）

        # xinggan 性感妹子
        # order = 1
        # for i in range(2, 111):
        #     request = Request(self.first_url.format(type='xinggan', pageNo=i), self.parse_pages)
        #     request.meta['order'] = order
        #     yield request
        #
        # # japan 日本妹子
        # order = 2
        # for i in range(2, 28):
        #     request = Request(self.first_url.format(type='japan', pageNo=i), self.parse_pages)
        #     request.meta['order'] = order
        #     yield request
        #
        # # taiwan 台湾妹子
        # order = 3
        # for i in range(2, 11):
        #     request = Request(self.first_url.format(type='taiwan', pageNo=i), self.parse_pages)
        #     request.meta['order'] = order
        #     yield request
        #
        # # mm 清纯妹子
        # order = 4
        # for i in range(2, 31):
        #     request = Request(self.first_url.format(type='mm', pageNo=i), self.parse_pages)
        #     request.meta['order'] = order
        #     yield request

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.mzitu.com',
            'Referer': 'http://www.mzitu.com/zipai/',
        }
        request = Request(url='http://www.mzitu.com/xinggan/page/2/', headers=headers, callback=self.parse_pages)
        request.meta['order'] = 1
        yield request

    '''
    处理每页内容
    '''
    def parse_pages(self, response):
        # print(response.text)
        order = response.meta['order']

        data = response.css('#pins > li')
        if data:
            # print(data)
            for li in data:
                url = li.css('a::attr(href)').extract_first()

                item = PictureItem()
                # 设置类型名称
                item['type_name'] = '性感美女'

                self.process_picture_response(li, item)
                # yield item
                request = Request(url, self.parse_picture_detail)
                request.meta['pictureItem'] = item
                yield request

    '''
    提取picture response信息
    '''
    def process_picture_response(self, li, item):
        # print(li.extract())
        item['name'] = li.css('a > img::attr(alt)').extract_first().strip()
        # 处理类型 type_id

        item['logo_url'] = li.css('a > img::attr(data-original)').extract_first().strip()
        # 提取数据来源 (mzitu)
        item['source'] = '妹子图'
        # 源站 url
        item['station_url'] = li.css('a::attr(href)').extract_first()

        # 提取源站影片ID
        result = re.search('/(\d+)', item['station_url'])
        if result:
            item['station_pic_id'] = result.group(1).strip()
        else:
            item['station_pic_id'] = ''

    '''
    处理图片详情页信息(带分页信息)
    '''
    def parse_picture_detail(self, response):
        # print(response.text)
        item = response.meta['pictureItem']

        total_page = response.css('body > div.main > div.content > div.pagenavi > a:nth-last-child(2) > span::text')
        if total_page:
            total_page = total_page.extract_first().strip()
        else:  # 无分页的情况
            request = Request(response.url, self.process_url_response)
            request.meta['pictureItem'] = item
            yield request
            return

        first_url = response.url
        for i in range(1, int(total_page) + 1):
            url = ''
            if i == 1:
                url = first_url
            else:
                url = first_url + '/' + str(i)

            request = Request(url, self.process_url_response)
            request.meta['pictureItem'] = item
            request.meta['order'] = str(i)
            yield request

    '''
    提取url response信息
    '''
    def process_url_response(self, response):
        # print(response.text)
        pictureItem = response.meta['pictureItem']
        order = response.meta['order']

        urlList = []
        imgList = response.css('body > div.main > div.content > div.main-image > p > a > img')
        if imgList:
            for img in imgList:
                item = PictureUrlItem()
                item['url'] = img.css('::attr(src)').extract_first().strip()
                # 排序信息
                item['order'] = order
                urlList.append(item)
                # print(item)

        pictureItem['picture_urls'] = urlList
        # print(pictureItem)
        yield pictureItem