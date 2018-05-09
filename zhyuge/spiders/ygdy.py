# -*- coding: utf-8 -*-
import hashlib
import re

import scrapy
from scrapy import Request
from scrapy.utils.python import to_bytes

from zhyuge.common.string_utils import StringUtils
from zhyuge.items import MiaozMovieItem, ImageItem

'''
阳光电影Spider
'''
class YgdySpider(scrapy.Spider):
    name = 'ygdy'
    allowed_domains = ['www.ygdy8.com']
    start_urls = ['http://www.ygdy8.com/']

    # 阳光电影基地址
    base_url = 'http://www.ygdy8.com'

    '''
    电影起始URL：参数顺序依次为：
    '''
    index_url = 'http://www.ygdy8.com/html/gndy/dyzz/index.html'
    first_url = 'http://www.ygdy8.com/html/gndy/dyzz/list_23_{page_no}.html'
    #  电影总页数
    total_page = 1

    '''
    电视剧起始URL：参数顺序依次为：
    '''
    # 华语电视剧相关
    huayu_index_url = 'http://www.ygdy8.com/html/tv/hytv/index.html'
    huayu_first_url = 'http://www.ygdy8.com/html/tv/hytv/list_71_{page_no}.html'
    huayu_total_page = 1

    # 日韩电视剧相关
    rihan_index_url = 'http://www.ygdy8.com/html/tv/rihantv/index.html'
    rihan_first_url = 'http://www.ygdy8.com/html/tv/rihantv/list_8_{page_no}.html'
    rihan_total_page = 1

    # 欧美电视剧相关
    oumei_index_url = 'http://www.ygdy8.com/html/tv/oumeitv/index.html'
    oumei_first_url = 'http://www.ygdy8.com/html/tv/oumeitv/list_9_{page_no}.html'
    oumei_total_page = 1
    

    '''
    classify: 0 电影、1 电视剧
    drama: 0 华语、1 日韩、2 欧美
    '''
    def start_requests(self):
        # 获取电影
        yield Request(self.index_url, self.get_movie_pages)
        # 获取华语电视剧
        yield Request(self.huayu_index_url, self.get_huayu_pages)
        # 获取日韩电视剧
        yield Request(self.rihan_index_url, self.get_rihan_pages)
        # 获取欧美电视剧
        yield Request(self.oumei_index_url, self.get_oumei_pages)

    '''
    获取电影数据
    '''
    def get_movie_pages(self, response):
        # print(response.text)
        result = re.search('共(.*?)页', response.text)
        if result:
            self.total_page = int(result.group(1).strip())

        # 抓取电影数据
        for page_no in range(1, self.total_page):
        # for page_no in range(1, 2):
            request = Request(self.first_url.format(page_no=page_no), self.parse_pages)
            request.meta['classify'] = 0
            yield request

    '''
    获取华语电视剧数据
    '''
    def get_huayu_pages(self, response):
        # print(response.text)
        result = re.search('共(.*?)页', response.text)
        if result:
            self.huayu_total_page = int(result.group(1).strip())

        # 抓取数据
        for page_no in range(1, self.huayu_total_page):
        # for page_no in range(1, 2):
            request = Request(self.huayu_first_url.format(page_no=page_no), self.parse_pages)
            request.meta['classify'] = 1
            request.meta['drama'] = 0
            yield request

    '''
    获取日韩电视剧数据
    '''
    def get_rihan_pages(self, response):
        # print(response.text)
        result = re.search('共(.*?)页', response.text)
        if result:
            self.rihan_total_page = int(result.group(1).strip())

        # 抓取数据
        for page_no in range(1, self.rihan_total_page):
        # for page_no in range(1, 2):
            request = Request(self.rihan_first_url.format(page_no=page_no), self.parse_pages)
            request.meta['classify'] = 1
            request.meta['drama'] = 1
            yield request

    '''
    获取欧美电视剧数据
    '''
    def get_oumei_pages(self, response):
        # print(response.text)
        result = re.search('共(.*?)页', response.text)
        if result:
            self.oumei_total_page = int(result.group(1).strip())

        # 抓取数据
        for page_no in range(1, self.huayu_total_page):
        # for page_no in range(1, 2):
            request = Request(self.oumei_first_url.format(page_no=page_no), self.parse_pages)
            request.meta['classify'] = 1
            request.meta['drama'] = 2
            yield request

    '''
    处理每页内容
    '''
    def parse_pages(self, response):
        # print(response.text)
        classify = response.meta['classify']
        data = response.css('#header > div > div.bd2 > div.bd3 > div.bd3r > div.co_area2 > div.co_content8 > ul')
        if data.css('table'):
            list = data.css('table .ulink::attr(href)').extract()
            for url in list:
                full_url = self.base_url + url
                func = None
                if classify == 0:  # 拉取电影
                    func = self.parse_movie_detail
                elif classify == 1:  # 拉取电视剧
                    func = self.parse_teleplay_detail
                request = Request(full_url, func)
                request.meta['drama'] = response.meta['drama']
                yield request

    '''
    处理电影详情页信息
    '''
    def parse_movie_detail(self, response):
        # print(response.text)
        item = MiaozMovieItem()
        self.process_movie_response(response, item)
        item['type'] = 1

        # 生成图片下载Request
        imageItem = ImageItem()
        image_urls = [item['logo_url']]
        imageItem['image_urls'] = image_urls
        # 图片实际保存路径
        image_guid = hashlib.sha1(to_bytes(item['logo_url'])).hexdigest()
        imageItem['real_url'] = 'images/ygdy/%s.jpg' % (image_guid)
        imageItem['thumb_url'] = 'thumbs/ygdy/%s.jpg' % (image_guid)
        item['logo_url'] = '/' + imageItem['thumb_url']

        yield item
        yield imageItem

    '''
    提取电影response信息
    '''
    def process_movie_response(self, response, item):
        # 提取电影名称
        name = response.css('#header > div > div.bd2 > div.bd3 > div.bd3r > div.co_area2 > div.title_all > h1 > font').extract_first()
        if name:
            result = re.search('《(.*?)》', name)
            if result:
                item['name'] = result.group(1).strip()
        else:
            item['name'] = ''
        # 提取上映年份
        result = re.search('年　　代(.*?)<', response.text)
        if result:
            item['year'] = result.group(1).strip()
        else:
            item['year'] = ''
        # 提取logo_url
        zoom = response.css('#Zoom').extract_first()
        result = re.search('<img .*?src="(.*?)".*?>', zoom)
        if result:
            item['logo_url'] = result.group(1).strip()
        else:
            item['logo_url'] = ''
        # 提取评分
        result = re.search('豆瓣评分(.*?)/10 from', response.text)
        if result:
            item['score'] = result.group(1).strip()
        else:
            result = re.search('IMDb评分(.*?)/10 from', response.text)
            if result:
                item['score'] = result.group(1).strip()
            else:
                item['score'] = ''
        # 提取导演信息
        result = re.search('导　　演(.*?)<', response.text)
        if result:
            item['director'] = result.group(1).strip()
            item['director'] = item['director'].replace('&middot;', '·')
        else:
            item['director'] = ''
        # 提取编剧信息（暂无）
        item['playwright'] = ''
        # 提取演员信息
        result = re.search('主　　演(.*?)<br /><br />', response.text)
        if result:
            item['actor'] = result.group(1).strip()

            actorStr = ''
            actorList = item['actor'].split('<br />')
            for actor in actorList:
                if actorStr == '':
                    actorStr = actor.strip()
                else:
                    actorStr = actorStr + '、' + actor.strip()
            item['actor'] = actorStr.strip()
            item['actor'] = item['actor'].replace('&middot;', '·')
        else:
            item['actor'] = ''
        # 提取类型信息
        result = re.search('类　　别(.*?)<', response.text)
        if result:
            item['type_ids'] = result.group(1).strip()
            item['type_ids'] = item['type_ids'].replace('/', ',')
            item['type_ids'] = item['type_ids'].replace('】', '')
            item['type_ids'] = item['type_ids'].replace('&nbsp;', '')
            item['type_ids'] = item['type_ids'].replace('：', '')
        else:
            item['type_ids'] = ''
        # 提取国家信息
        result = re.search('产　　地(.*?)<', response.text)
        if result:
            item['region_ids'] = result.group(1).strip()
        else:
            result = re.search('国　　家(.*?)<', response.text)
            if result:
                item['region_ids'] = result.group(1).strip()
            else:
                item['region_ids'] = ''
        # 提取语言信息
        result = re.search('语　　言(.*?)<', response.text)
        if result:
            item['language'] = result.group(1).strip()
        else:
            item['language'] = ''
        # 提取上映日期
        result = re.search('发布时间：(.*?)<tr>', response.text, re.S)
        if result:
            item['release_date'] = result.group(1).strip()
        else:
            item['release_date'] = ''
        # 提取片长
        result = re.search('片　　长(.*?)<', response.text)
        if result:
            item['length'] = result.group(1).strip()
        else:
            item['length'] = ''
        # 提取英文名
        result = re.search('译　　名(.*?)<', response.text)
        if result:
            item['en_name'] = result.group(1).strip()
        else:
            item['en_name'] = ''
        # 提取剧情简介
        result = re.search('简　　介.*?<br /><br />(.*?)<br /><br /><img', response.text)
        if result:
            item['introduction'] = result.group(1).strip()
        else:
            item['introduction'] = ''
        # 提取数据来源
        item['source'] = '阳光电影'
        # 提取源站影片ID
        result = re.search('/(\d+).html', response.url)
        if result:
            item['station_movie_id'] = result.group(1).strip()
        else:
            item['station_movie_id'] = ''
        # 提取下载链接
        downloadUrls = response.css('#Zoom > td > table')
        urlList = []
        for downloadUrl in downloadUrls:
            temp_url = downloadUrl.css('tr > td > a::text').extract_first()
            try:
                if temp_url.index('://'):
                    urlList.append(temp_url)
            except:
                pass
        item['download_urls'] = urlList
        # 源站链接
        item['station_url'] = response.url



    '''
    处理电视剧详情页信息
    '''
    def parse_teleplay_detail(self, response):
        # print(response.text)
        item = MiaozMovieItem()
        drama = response.meta['drama']
        if drama == 0: # 华语
            self.process_huayu_response(response, item)
        elif drama == 1: # 日韩
            self.process_rihan_response(response, item)
        else: # 欧美
            self.process_oumei_response(response, item)
        item['type'] = 2

        # 生成图片下载Request
        imageItem = ImageItem()
        image_urls = [item['logo_url']]
        imageItem['image_urls'] = image_urls
        # 图片实际保存路径
        image_guid = hashlib.sha1(to_bytes(item['logo_url'])).hexdigest()
        imageItem['real_url'] = 'images/ygdy/%s.jpg' % (image_guid)
        imageItem['thumb_url'] = 'thumbs/ygdy/%s.jpg' % (image_guid)
        item['logo_url'] = '/' + imageItem['real_url']

        yield item
        yield imageItem

    '''
    提取华语电视剧response信息
    '''
    def process_huayu_response(self, response, item):
        # 提取电影名称
        name = response.css('#header > div > div.bd2 > div.bd3 > div.bd3r > div.co_area2 > div.title_all > h1 > font').extract_first()
        if name:
            result = re.search('《(.*?)》', name)
            if result:
                item['name'] = result.group(1).strip()
        else:
            item['name'] = ''
        # 提取上映年份
        result = re.search('年　　代(.*?)<', response.text)
        if result:
            item['year'] = result.group(1).strip()
            item['year'] = StringUtils.filter_charactor(item['year'])
        else:
            item['year'] = ''
        # 提取logo_url
        zoom = response.css('#Zoom').extract_first()
        result = re.search('<img .*?src="(.*?)".*?>', zoom)
        if result:
            item['logo_url'] = result.group(1).strip()
        else:
            item['logo_url'] = ''
        # 提取评分
        result = re.search('豆瓣评分(.*?)/10 from', response.text)
        if result:
            item['score'] = result.group(1).strip()
        else:
            result = re.search('IMDb评分(.*?)/10 from', response.text)
            if result:
                item['score'] = result.group(1).strip()
            else:
                item['score'] = ''
        # 提取导演信息
        result = re.search('导　　演(.*?)<', response.text)
        if result:
            item['director'] = result.group(1).strip()
            item['director'] = item['director'].replace('&middot;', '·')
        else:
            item['director'] = ''
        # 提取编剧信息（暂无）
        item['playwright'] = ''
        # 提取演员信息
        result = re.search('主　　演(.*?)◎简　　介</p>', response.text, re.S)
        if result:
            item['actor'] = result.group(1).strip()
            item['actor'] = StringUtils.filter_tags(item['actor'])
            item['actor'] = item['actor'].replace('\r\n', '、')
            item['actor'] = item['actor'].replace('　', '')
            item['actor'] = item['actor'].replace('、 、', '')
        else:
            item['actor'] = ''
        # 提取类型信息
        result = re.search('类　　别(.*?)<', response.text)
        if result:
            item['type_ids'] = result.group(1).strip()
            item['type_ids'] = item['type_ids'].replace('/', ',')
            item['type_ids'] = item['type_ids'].replace('】', '')
            item['type_ids'] = item['type_ids'].replace('&nbsp;', '')
            item['type_ids'] = item['type_ids'].replace('：', '')
        else:
            item['type_ids'] = ''
        # 提取国家信息
        result = re.search('产　　地(.*?)<', response.text)
        if result:
            item['region_ids'] = result.group(1).strip()
        else:
            result = re.search('国　　家(.*?)<', response.text)
            if result:
                item['region_ids'] = result.group(1).strip()
            else:
                item['region_ids'] = ''
        # 提取语言信息
        result = re.search('语　　言(.*?)<', response.text)
        if result:
            item['language'] = result.group(1).strip()
            item['language'] = StringUtils.filter_charactor(item['language'])
        else:
            item['language'] = ''
        # 提取上映日期
        result = re.search('发布时间：(.*?)<tr>', response.text, re.S)
        if result:
            item['release_date'] = result.group(1).strip()
        else:
            item['release_date'] = ''
        # 提取片长
        result = re.search('片　　长(.*?)<', response.text)
        if result:
            item['length'] = result.group(1).strip()
        else:
            item['length'] = ''
        # 提取英文名
        result = re.search('译　　名(.*?)<', response.text)
        if result:
            item['en_name'] = result.group(1).strip()
        else:
            item['en_name'] = ''
        # 提取剧情简介
        result = re.search('简　　介(.*?)【下载地址】', response.text, re.S)
        if result:
            item['introduction'] = result.group(1).strip()
            item['introduction'] = StringUtils.filter_tags(item['introduction'])
            # item['actor'] = item['actor'].replace('\r\n', '、')
            # item['actor'] = item['actor'].replace('　', '')
            # item['actor'] = item['actor'].replace('、 、', '')
        else:
            item['introduction'] = ''
        # 提取数据来源
        item['source'] = '阳光电影'
        # 提取源站影片ID
        result = re.search('/(\d+).html', response.url)
        if result:
            item['station_movie_id'] = result.group(1).strip()
        else:
            item['station_movie_id'] = ''
        # 提取下载链接
        downloadUrls = response.css('table')
        urlList = []
        for downloadUrl in downloadUrls:
            temp_url = downloadUrl.css('tr > td > a::attr(href)').extract_first()
            try:
                if temp_url.index('://'):
                    urlList.append(temp_url)
            except:
                pass
        item['download_urls'] = urlList
        # 源站链接
        item['station_url'] = response.url

    '''
    提取日韩电视剧response信息
    '''
    def process_rihan_response(self, response, item):
        # 提取电影名称
        result = re.search('\[剧 名\]:(.*?)<br', response.text)
        if result:
            item['name'] = result.group(1).strip()
        else:
            item['name'] = ''
        # 提取上映年份
        item['year'] = response.css('#header > div > div.bd2 > div.bd3 > div.bd3r > div.co_area2 > div.title_all > h1 > font::text').extract_first()
        if item['year']:
            item['year'] = item['year'].strip()
            item['year'] = item['year'][:4]
        else:
            item['year'] = ''
        # 提取logo_url
        zoom = response.css('#Zoom').extract_first()
        result = re.search('<img .*?src="(.*?)".*?>', zoom)
        if result:
            item['logo_url'] = result.group(1).strip()
        else:
            item['logo_url'] = ''
        # 提取评分（暂无）
        result = re.search('豆瓣评分(.*?)/10 from', response.text)
        if result:
            item['score'] = result.group(1).strip()
        else:
            result = re.search('IMDb评分(.*?)/10 from', response.text)
            if result:
                item['score'] = result.group(1).strip()
            else:
                item['score'] = ''
        # 提取导演信息
        result = re.search('\[导 演\]:(.*?)<', response.text)
        if result:
            item['director'] = result.group(1).strip()
            item['director'] = item['director'].replace('&middot;', '·')
        else:
            item['director'] = ''
        # 提取编剧信息
        result = re.search('\[编 剧\]:(.*?)<', response.text)
        if result:
            item['playwright'] = result.group(1).strip()
            item['playwright'] = item['playwright'].replace('&middot;', '·')
        else:
            item['playwright'] = ''
        # 提取演员信息
        result = re.search('\[演 员\]:(.*?)<', response.text)
        if result:
            item['actor'] = result.group(1).strip()

            actorStr = ''
            actorList = item['actor'].split('<br />')
            for actor in actorList:
                if actorStr == '':
                    actorStr = actor.strip()
                else:
                    actorStr = actorStr + '、' + actor.strip()
            item['actor'] = item['actor'].replace('&middot;', '·')
            item['actor'] = actorStr.strip()
        else:
            item['actor'] = ''
        # 提取类型信息
        result = re.search('\[类 型\]:(.*?)<', response.text)
        if result:
            item['type_ids'] = result.group(1).strip()
        else:
            item['type_ids'] = ''
        # 提取国家信息
        item['region_ids'] = '日韩'
        # 提取语言信息（暂无）
        result = re.search('语　　言(.*?)<', response.text)
        if result:
            item['language'] = result.group(1).strip()
        else:
            item['language'] = ''
        # 提取上映日期
        result = re.search('发布时间：(.*?)<', response.text, re.S)
        if result:
            item['release_date'] = result.group(1).strip()
        else:
            item['release_date'] = ''
        # 提取片长（根据URLS处理）
        result = re.search('片　　长(.*?)<', response.text)
        if result:
            item['length'] = result.group(1).strip()
        else:
            item['length'] = ''
        # 提取英文名（暂无）
        result = re.search('译　　名(.*?)<', response.text)
        if result:
            item['en_name'] = result.group(1).strip()
        else:
            item['en_name'] = ''
        # 提取剧情简介
        result = re.search('\[简 介\]:(.*?)<', response.text)
        if result:
            item['introduction'] = result.group(1).strip()
        else:
            item['introduction'] = ''
        # 提取数据来源
        item['source'] = '阳光电影'
        # 提取源站影片ID
        result = re.search('/(\d+).html', response.url)
        if result:
            item['station_movie_id'] = result.group(1).strip()
        else:
            item['station_movie_id'] = ''
        # 提取下载链接
        downloadUrls = response.css('table')
        urlList = []
        for downloadUrl in downloadUrls:
            temp_url = downloadUrl.css('tr > td > a::attr(href)').extract_first()
            try:
                if temp_url.index('://'):
                    urlList.append(temp_url)
            except:
                pass
        item['download_urls'] = urlList
        # 源站链接
        item['station_url'] = response.url

    '''
    提取欧美电视剧response信息
    '''
    def process_oumei_response(self, response, item):
        # 提取电影名称
        item['name'] = response.css('#header > div > div.bd2 > div.bd3 > div.bd3r > div.co_area2 > div.title_all > h1 > font::text').extract_first()
        if item['name']:
            result = re.search('《(.*?)》', item['name'])
            if result:
                item['name'] = result.group(1).strip()
        else:
            item['name'] = ''
        # 提取上映年份
        item['year'] = response.css('#header > div > div.bd2 > div.bd3 > div.bd3r > div.co_area2 > div.title_all > h1 > font::text').extract_first()
        if item['year']:
            item['year'] = item['year'].strip()
            item['year'] = item['year'][:4]
        else:
            item['year'] = ''
        # 提取logo_url
        zoom = response.css('#Zoom').extract_first()
        result = re.search('<img .*?src="(.*?)".*?>', zoom)
        if result:
            item['logo_url'] = result.group(1).strip()
        else:
            item['logo_url'] = ''
        # 提取评分
        result = re.search('【IMDB评分】：(.*?)/10 from', response.text)
        if result:
            item['score'] = result.group(1).strip()
            item['score'] = StringUtils.filter_tags(item['score'])
        else:
            item['score'] = ''
        # 提取导演信息
        result = re.search('【导.*?演】：(.*?)【', response.text)
        if result:
            item['director'] = result.group(1).strip()
            item['director'] = StringUtils.filter_tags(item['director'])
        else:
            item['director'] = ''
        # 提取编剧信息
        result = re.search('【编.*?剧】：(.*?)【', response.text)
        if result:
            item['playwright'] = result.group(1).strip()
            item['playwright'] = StringUtils.filter_tags(item['playwright'])
        else:
            item['playwright'] = ''
        # 提取演员信息
        result = re.search('【演.*?员】：(.*?)【', response.text)
        if result:
            item['actor'] = result.group(1).strip()
            item['actor'] = StringUtils.filter_tags(item['actor'])
        else:
            item['actor'] = ''
        # 提取类型信息
        result = re.search('【类.*?别】：(.*?)【', response.text)
        if result:
            item['type_ids'] = result.group(1).strip()
            item['type_ids'] = StringUtils.filter_tags(item['type_ids'])
            item['type_ids'].replace('|', ',')
        else:
            item['type_ids'] = ''
        # 提取国家信息
        result = re.search('【国.*?家】：(.*?)【', response.text)
        if result:
            item['region_ids'] = result.group(1).strip()
            item['region_ids'] = StringUtils.filter_tags(item['region_ids'])
            item['region_ids'].replace('|', '/')
        else:
            item['region_ids'] = ''
        # 提取语言信息
        result = re.search('【语.*?言】：(.*?)【', response.text)
        if result:
            item['language'] = result.group(1).strip()
            item['language'] = StringUtils.filter_tags(item['language'])
        else:
            item['language'] = ''
        # 提取上映日期
        result = re.search('发布时间：(.*?)<tr>', response.text, re.S)
        if result:
            item['release_date'] = result.group(1).strip()
        else:
            item['release_date'] = ''
        # 提取片长
        result = re.search('片　　长(.*?)<', response.text)
        if result:
            item['length'] = result.group(1).strip()
        else:
            item['length'] = ''
        # 提取英文名
        result = re.search('【原.*?名】：(.*?)【', response.text)
        if result:
            item['en_name'] = result.group(1).strip()
            item['en_name'] = StringUtils.filter_tags(item['en_name'])
        else:
            item['en_name'] = ''
        # 提取剧情简介
        result = re.search('【简.*?介】：(.*?)【', response.text, re.S)
        if result:
            item['introduction'] = result.group(1).strip()
            item['introduction'] = StringUtils.filter_tags_without_br(item['introduction'])
        else:
            item['introduction'] = ''
        # 提取数据来源
        item['source'] = '阳光电影'
        # 提取源站影片ID
        result = re.search('/(\d+).html', response.url)
        if result:
            item['station_movie_id'] = result.group(1).strip()
        else:
            item['station_movie_id'] = ''
        # 提取下载链接
        downloadUrls = response.css('#Zoom > td > table')
        urlList = []
        for downloadUrl in downloadUrls:
            temp_url = downloadUrl.css('tr > td > a::text').extract_first()
            try:
                if temp_url.index('://'):
                    urlList.append(temp_url)
            except:
                pass
        item['download_urls'] = urlList
        # 源站链接
        item['station_url'] = response.url

