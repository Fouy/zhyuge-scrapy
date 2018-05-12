# -*- coding: utf-8 -*-
import hashlib
import json
import re

import scrapy
from scrapy import Request
from scrapy.utils.python import to_bytes

from zhyuge.items import MiaozMovieItem, ImageItem

'''
喵爪电影更新爬虫
'''
class MiaozupdateSpider(scrapy.Spider):
    name = 'miaozupdate'
    allowed_domains = ['www.miao-z.com']
    start_urls = ['http://www.miao-z.com/']

    # 喵爪电影基地址
    base_url = 'http://www.miao-z.com'
    # 电影起始URL：首页最新更新的10页
    first_movie_url = 'http://www.miao-z.com/latest_json?pn={pn}'
    # 电视剧起始URL：电视剧最新的10页
    first_drama_url = 'http://www.miao-z.com/tv?pn={pn}'
    # 详情页地址
    detail_url = 'http://www.miao-z.com/detail/{id}'

    '''
    开始请求列表
    '''
    def start_requests(self):
        # 抓取电影数据
        for pn in range(10):
            request = Request(self.first_movie_url.format(pn=pn+1), self.parse_pages)
            request.meta['classify'] = 0
            yield request

        # request = Request(self.first_movie_url.format(pn=1), self.parse_pages)
        # request.meta['classify'] = 0
        # yield request

        # 抓取电视剧数据
        for pn in range(10):
            request = Request(self.first_drama_url.format(pn=pn+1), self.parse_pages)
            request.meta['classify'] = 1
            yield request

    '''
    处理每页内容
    '''
    def parse_pages(self, response):
        # print(response.text)
        classify = response.meta['classify']
        if classify == 0:  # 拉取电影
            movies = json.loads(response.body_as_unicode())
            for movie in movies:
                yield Request(self.detail_url.format(id=movie['id']), self.parse_movie_detail)
        elif classify == 1:  # 拉取电视剧
            data = response.css('#content > div > div.article > div:nth-child(1)')
            if data.css('table'):
                list = data.css('table .nbg::attr(href)').extract()
                for url in list:
                    full_url = self.base_url + url
                    yield Request(full_url, self.parse_teleplay_detail)


    '''
    处理电影详情页信息
    '''
    def parse_movie_detail(self, response):
        # print(response.text)
        item = MiaozMovieItem()
        self.process_response(response, item)
        item['type'] = 1

        # 生成图片下载Request
        imageItem = ImageItem()
        image_urls = [item['logo_url']]
        imageItem['image_urls'] = image_urls
        # 图片实际保存路径
        image_guid = hashlib.sha1(to_bytes(item['logo_url'])).hexdigest()
        imageItem['real_url'] = 'images/miaoz/%s.jpg' % (image_guid)
        imageItem['thumb_url'] = 'thumbs/miaoz/%s.jpg' % (image_guid)
        item['logo_url'] = '/' + imageItem['real_url']

        yield item
        yield imageItem

    '''
    处理电视剧详情页信息
    '''
    def parse_teleplay_detail(self, response):
        # print(response.text)
        item = MiaozMovieItem()
        self.process_response(response, item)
        item['type'] = 2

        # 生成图片下载Request
        imageItem = ImageItem()
        image_urls = [item['logo_url']]
        imageItem['image_urls'] = image_urls
        # 图片实际保存路径
        image_guid = hashlib.sha1(to_bytes(item['logo_url'])).hexdigest()
        imageItem['real_url'] = 'images/miaoz/%s.jpg' % (image_guid)
        imageItem['thumb_url'] = 'thumbs/miaoz/%s.jpg' % (image_guid)
        item['logo_url'] = '/' + imageItem['real_url']

        yield item
        yield imageItem

    '''
    提取response信息
    '''
    def process_response(self, response, item):
        item['name'] = response.css('#content > h1 > span:nth-child(1)::text').extract_first().strip()
        item['year'] = response.css('#content > h1 > span.year::text').extract_first()[1:-1].strip()
        item['logo_url'] = self.base_url + response.css('#mainpic > img::attr(src)').extract_first()
        item['score'] = response.css('#info > span.rating_nums::text').extract_first()
        item['director'] = response.css('#info > span:nth-child(4) > span.attrs > a::text').extract_first()
        # 提取编剧信息
        playwriteList = response.css('#info > span:nth-child(6) > span.attrs > a')
        playwriteStr = ''
        for playwrite in playwriteList:
            if playwriteStr == '':
                playwriteStr = playwrite.css('::text').extract_first()
            else:
                playwriteStr = playwriteStr + '、' + playwrite.css('::text').extract_first()
        if playwriteStr and playwriteStr != '':
            playwriteStr = playwriteStr.strip()
        item['playwright'] = playwriteStr
        # 提取演员信息
        actorList = response.css('#info > span.actor > span.attrs > a')
        actorStr = ''
        for actor in actorList:
            if actorStr == '':
                actorStr = actor.css('::text').extract_first()
            else:
                actorStr = actorStr + '、' + actor.css('::text').extract_first()
        if actorStr and actorStr != '':
            actorStr = actorStr.strip()
        item['actor'] = actorStr
        # 提取类型信息
        item['type_ids'] = response.css('#info > span[property="v:genre"]::text').extract_first().strip()
        # 提取国家信息
        result = re.search('<span class="pl">制片国家/地区:</span>(.*?)<br>', response.text)
        if result:
            item['region_ids'] = result.group(1).strip()
        else:
            item['region_ids'] = ''
        # 提取语言信息
        result = re.search('<span class="pl">语言:</span>(.*?)<br>', response.text)
        if result:
            item['language'] = result.group(1).strip()
        else:
            item['language'] = ''
        # 提取上映日期
        result = re.search('<span class="pl">上映日期:</span> <span>(.*?)</span><br>', response.text)
        if result:
            item['release_date'] = result.group(1).strip()
        else:
            item['release_date'] = ''
        # 提取片长
        result = re.search('<span class="pl">片长:</span> <span>(.*?)</span><br>', response.text)
        if result:
            item['length'] = result.group(1).strip()
        else:
            item['length'] = ''
        # 提取英文名
        result = re.search('<span class="pl">又名:</span>(.*?)<br>', response.text)
        if result:
            item['en_name'] = result.group(1).strip()
        else:
            item['en_name'] = ''
        # 提取剧情简介
        item['introduction'] = response.css('#link-report').extract_first()
        # 提取数据来源 (喵爪)
        item['source'] = '喵爪电影'
        # result = re.search('<p style="text-indent:2em">数据来源:(.*?)</p>', response.text)
        # if result:
        #     item['source'] = result.group(1).strip()
        # else:
        #     item['source'] = ''
        # 提取源站影片ID
        result = re.search('/static/poster/s/(\d+).jpg', item['logo_url'])
        if result:
            item['station_movie_id'] = result.group(1).strip()
        else:
            item['station_movie_id'] = ''

        # 提取下载链接
        downloadUrls = response.css('table > tr')
        urlList = []
        for downloadUrl in downloadUrls:
            temp_url = downloadUrl.css('td:nth-child(1) > p::text').extract_first()
            try:
                if temp_url.find('://') or temp_url.find('magnet'):
                    urlList.append(temp_url)
            except:
                pass
        item['download_urls'] = urlList
        # 源站链接
        item['station_url'] = response.url
