# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request

from zhyuge.items import PictureItem, PictureUrlItem

'''
jingdiantu经典图Spider
'''
class JingdiantuSpider(scrapy.Spider):
    name = 'jingdiantu'
    allowed_domains = ['www.jingdiantu.com']
    start_urls = ['https://www.jingdiantu.com/']

    # jingdiantu图片基地址
    base_url = 'https://www.jingdiantu.com'
    '''
    起始URL：参数顺序依次为：
        分类：性感美女 网络美女 唯美写真 丝袜美腿 模特美女 动漫美女 体育美女
    '''
    first_url = 'https://www.jingdiantu.com/list-{type}-{pageNo}.html'
    typeList = ['性感美女', '网络美女', '唯美写真', '丝袜美腿', '模特美女', '动漫美女', '体育美女']

    protocol = 'https:'

    '''
    开始请求列表
    '''
    def start_requests(self):
        # 抓取图片数据
        order = 1
        for type in self.typeList:
            for i in range(1, 1042):
                request = Request(self.first_url.format(type=type, pageNo=i), self.parse_pages)
                request.meta['order'] = order
                yield request
            order += 1

        # request = Request(self.first_url.format(type='性感美女', pageNo=1), self.parse_pages)
        # request.meta['order'] = 1
        # yield request

    '''
    处理每页内容
    '''
    def parse_pages(self, response):
        # print(response.text)
        order = response.meta['order']

        data = response.css('body > div.mainer > div.piclist > ul > li')
        if data :
            # print(data)
            for li in data:
                url = self.protocol + li.css('a::attr(href)').extract_first()

                item = PictureItem()
                # 设置类型名称
                if order == 1:
                    item['type_name'] = '性感美女'
                elif order == 2:
                    item['type_name'] = '性感美女'
                elif order == 3:
                    item['type_name'] = '唯美写真'
                elif order == 4:
                    item['type_name'] = '高跟丝袜'
                elif order == 5:
                    item['type_name'] = '模特美女'
                elif order == 6:
                    item['type_name'] = '动漫美女'
                elif order == 7:
                    item['type_name'] = '体育美女'


                self.process_picture_response(li, item)
                # yield item
                request = Request(url, self.parse_picture_detail)
                request.meta['pictureItem'] = item
                # print(item)
                yield request

    '''
    提取picture response信息
    '''
    def process_picture_response(self, li, item):
        item['name'] = li.css('a > span::text').extract_first().strip()
        # 处理类型 type_id

        item['logo_url'] = self.protocol + li.css('a > img::attr(lazysrc)').extract_first().strip()
        # 提取数据来源 (jingdiantu)
        item['source'] = '经典图'
        # 源站 url
        item['station_url'] = self.protocol + li.css('a::attr(href)').extract_first()

        # 提取源站图片ID
        result = re.search('/tu-(\d+).html', item['station_url'])
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

        total_page = response.css('#allnum::text')
        if total_page:
            total_page = total_page.extract_first().strip()
        else: # 无分页的情况, 一张图片直接丢弃
            return

        first_url = response.url
        for i in range(1, int(total_page)+1):
            url = 'https://www.jingdiantu.com/tu-{stationId}-{pageNo}.html'
            url = url.format(stationId = item['station_pic_id'], pageNo = i)

            request = Request(url, self.process_url_response)
            request.meta['pictureItem'] = item
            request.meta['order'] = i
            yield request


    '''
    提取url response信息
    '''
    def process_url_response(self, response):
        # print(response.text)
        pictureItem = response.meta['pictureItem']
        order = response.meta['order']

        urlList = []
        imgList = response.css('body > div.mainer > div.picmainer > div.picsbox.picsboxcenter > p > img')
        if imgList:
            for img in imgList:
                item = PictureUrlItem()
                item['url'] = self.protocol + img.css('::attr(lazysrc)').extract_first().strip()
                # 排序信息
                item['order'] = order
                urlList.append(item)
                # print(item)

        pictureItem['picture_urls'] = urlList
        # print(pictureItem)
        yield pictureItem

