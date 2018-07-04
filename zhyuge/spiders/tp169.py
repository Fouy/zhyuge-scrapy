# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request

from zhyuge.items import PictureItem, PictureUrlItem

'''
169tp图片Spider
'''
class Tp169Spider(scrapy.Spider):
    name = 'tp169'
    allowed_domains = ['www.169we.com']
    start_urls = ['http://www.169we.com/']

    # 169tp图片基地址
    base_url = 'http://www.169we.com'
    '''
    起始URL：参数顺序依次为：
        分类：xingganmeinv 性感美女、wangyouzipai 网友自拍、gaogensiwa 高跟丝袜、xiyangmeinv 西洋美女、guoneimeinv 国内美女
    '''
    first_url = 'http://www.169we.com/{type}/list_{order}_{pageNo}.html'
    typeList = ['xingganmeinv', 'wangyouzipai', 'gaogensiwa', 'xiyangmeinv', 'guoneimeinv']

    '''
    开始请求列表
    '''
    def start_requests(self):
        # 抓取图片数据
        # order = 1
        # for type in self.typeList:
        #     for i in range(1, 1000):
        #         request = Request(self.first_url.format(type=type, order=order, pageNo=i), self.parse_pages)
        #         request.meta['order'] = order
        #         yield request
        #     order += 1

        request = Request(self.first_url.format(type='xingganmeinv', order=1, pageNo=2), self.parse_pages)
        request.meta['order'] = 1
        yield request

    '''
    处理每页内容
    '''
    def parse_pages(self, response):
        # print(response.text)
        order = response.meta['order']

        data = response.css('body > div:nth-child(8) > ul > li')
        if data :
            # print(data)
            for li in data:
                url = li.css('a::attr(href)').extract_first()

                item = PictureItem()
                # 设置类型名称
                if order == 1:
                    item['type_name'] = '性感美女'
                elif order == 2:
                    item['type_name'] = '网友自拍'
                elif order == 3:
                    item['type_name'] = '高跟丝袜'
                elif order == 4:
                    item['type_name'] = '西洋美女'
                elif order == 5:
                    item['type_name'] = '国内美女'

                self.process_picture_response(li, item)
                # yield item
                request = Request(url, self.parse_picture_detail)
                request.meta['pictureItem'] = item
                yield request

    '''
    提取picture response信息
    '''
    def process_picture_response(self, li, item):
        item['name'] = li.css('p::text').extract_first().strip()
        # 处理类型 type_id

        item['logo_url'] = li.css('img::attr(src)').extract_first().strip()
        # 提取数据来源 (169tp)
        item['source'] = '169美女'
        # 源站 url
        item['station_url'] = li.css('a::attr(href)').extract_first()

        # 提取源站影片ID
        result = re.search('/(\d+).html', item['station_url'])
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

        total_page = response.css('#content > div.big-pic > div.dede_pages > ul > li:nth-child(1) > a::text')
        if total_page:
            total_page = total_page.extract_first().strip()
        else: # 无分页的情况
            request = Request(response.url, self.process_url_response)
            request.meta['pictureItem'] = item
            yield request
            return

        result = re.search('共(.*?)页', total_page)
        if result:
            total_page = result.group(1).strip()

            first_url = response.url
            for i in range(1, int(total_page)+1):
                url = ''
                if i == 1 :
                    url = first_url
                else :
                    url = first_url[0:-5] + '_' + str(i) + '.html'

                request = Request(url, self.process_url_response)
                request.meta['pictureItem'] = item
                yield request


    '''
    提取url response信息
    '''
    def process_url_response(self, response):
        # print(response.text)
        pictureItem = response.meta['pictureItem']

        urlList = []
        imgList = response.css('#content > div.big-pic > div.big_img > p > img')
        if imgList:
            for img in imgList:
                item = PictureUrlItem()
                item['url'] = img.css('::attr(src)').extract_first().strip()
                # 排序信息
                result = re.search('/(\d*?).jpg', item['url'])
                if result:
                    item['order'] = result.group(1).strip()
                else:
                    item['order'] = ''
                urlList.append(item)
                # print(item)

        pictureItem['picture_urls'] = urlList
        # print(pictureItem)
        yield pictureItem


