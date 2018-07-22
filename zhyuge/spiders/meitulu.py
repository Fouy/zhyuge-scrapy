# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request

from zhyuge.items import PictureItem, PictureUrlItem

'''
美图录 图片Spider
'''
class MeituluSpider(scrapy.Spider):
    name = 'meitulu'
    allowed_domains = ['www.meitulu.com']
    start_urls = ['http://www.meitulu.com/']

    # 美图录 图片基地址
    base_url = 'http://www.meitulu.com'
    '''
    起始URL：参数顺序依次为：
        分类：nvshen 女神 jipin 极品 nenmo 嫩模 wangluohongren 网络红人 fengsuniang 风俗娘 qizhi 气质 youwu 尤物
        baoru 爆乳 xinggan 性感 youhuo 诱惑 meixiong 美胸 shaofu 少妇 changtui 长腿 mengmeizi 萌妹子
        luoli 萝莉 keai 可爱 huwai 户外 bijini 比基尼 qingchun 清纯 weimei 唯美 qingxin 清新
    '''
    # first_url = 'https://www.meitulu.com/t/{type}/{pageNo}.html'
    # typeList = ['nvshen', 'jipin', 'nenmo', 'wangluohongren', 'fengsuniang', 'qizhi', 'youwu',
    #     'baoru', 'xinggan', 'youhuo', 'meixiong', 'shaofu', 'changtui', 'mengmeizi',
    #     'luoli', 'keai', 'huwai', 'bijini', 'qingchun', 'weimei', 'qingxin' ]

    first_url = 'https://www.meitulu.com/{type}/{pageNo}.html'
    typeList = ['rihan', 'gangtai', 'guochan']

    '''
    开始请求列表
    '''
    def start_requests(self):
        # 抓取图片数据
        order = 1

        # 全量数据
        # for type in self.typeList:
        #     for i in range(1, 139):
        #         request = Request(self.first_url.format(type=type, pageNo=i), self.parse_pages)
        #         request.meta['order'] = order
        #         yield request
        #     order += 1

        # 增量数据
        added_url = 'https://www.meitulu.com/{type}/'
        for type in self.typeList:
            request = Request(added_url.format(type=type), self.parse_pages)
            request.meta['order'] = order
            yield request
            order += 1


    '''
    处理每页内容
    '''
    def parse_pages(self, response):
        # print(response.text)
        order = response.meta['order']

        data = response.css('body > div.main > div.boxs > ul > li')
        if data:
            # print(data)
            for li in data:
                url = li.css('a::attr(href)').extract_first()

                item = PictureItem()
                # 设置类型名称
                # item['type_name'] = '性感美女'
                if order == 1:
                    item['type_name'] = '日韩美女'
                elif order == 2:
                    item['type_name'] = '港台美女'
                elif order == 3:
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
        item['name'] = li.css('p.p_title > a::text').extract_first().strip()
        # 处理类型 type_id

        item['logo_url'] = li.css('a > img::attr(src)').extract_first().strip()
        # 提取数据来源 (美图录)
        item['source'] = '美图录'
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

        # 假设为 42页大小
        total_page = '42'

        first_url = response.url
        for i in range(1, int(total_page) + 1):
            url = ''
            if i == 1:
                url = first_url
            else:
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
        imgList = response.css('body > div.content > center > img')
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
