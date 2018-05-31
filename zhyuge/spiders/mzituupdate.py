# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request

from zhyuge.items import PictureItem, PictureUrlItem

'''
妹子图Spider (更新)
'''
class MzituupdateSpider(scrapy.Spider):
    name = 'mzituupdate'
    allowed_domains = ['www.mzitu.com']
    start_urls = ['http://www.mzitu.com/']

    # 更新的条数
    updateCount = 50

    '''
    开始请求列表
    '''
    def start_requests(self):
        # 抓取图片数据（更新）
        request = Request('http://www.mzitu.com/all/', self.parse_pages)
        yield request

    '''
    处理每页内容
    '''
    def parse_pages(self, response):
        # print(response.text)
        data = response.css('div.all ul.archives a')
        if data:
            # print(data.extract())
            # 只拉取10条
            for i in range(0, self.updateCount):
                # print(data[i].extract())
                aStr = data[i].extract()
                item = PictureItem()
                # 设置类型名称
                item['type_name'] = '性感美女'
                # 提取URL
                url = ''
                result = re.search('href="(.*?)" target', aStr)
                if result:
                    url = result.group(1).strip()
                else:
                    break

                self.process_picture_response(aStr, item)
                # yield item
                request = Request(url, self.parse_picture_detail)
                request.meta['pictureItem'] = item
                yield request




    '''
    提取picture response信息
    '''
    def process_picture_response(self, aStr, item):
        # print(li.extract())
        result = re.search('<a.*?>(.*?)</a>', aStr)
        item['name'] = result.group(1).strip()

        item['logo_url'] = ''
        # 提取数据来源 (mzitu)
        item['source'] = '妹子图'
        # 源站 url
        result = re.search('href="(.*?)" target', aStr)
        item['station_url'] = result.group(1).strip()

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