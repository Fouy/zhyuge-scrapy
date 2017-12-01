# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy import Request

from zhyuge.items import MiaozMovieItem, MiaozTeleplayItem, ImageItem

'''
喵爪电影Spider
'''
class MiaozSpider(scrapy.Spider):
    name = 'miaoz'
    allowed_domains = ['www.miao-z.com']
    start_urls = ['http://www.miao-z.com/']

    # 喵爪电影基地址
    base_url = 'http://www.miao-z.com'
    '''
    起始URL：参数顺序依次为：
        分类：0电影 1电视剧、
        类型：1爱情 2喜剧 3动画 4剧情 5科幻 6动作 7悬疑 8犯罪 9惊悚 10恐怖 11战争 12情色 13音乐、
        地区：1中国 2美国 3英国 4日本 5韩国 6法国、
        年份：2017 2016 2015 2014 2013 2012 2011 2010 2009 2008 2007 2006
    '''
    first_url = 'http://www.miao-z.com/list/{classify}-{type}-{region}-{year}-1-1.html'
    classifyList = [0, 1]
    typeList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    regionList = [1, 2, 3, 4, 5, 6]
    yearList = [2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006]

    '''
    开始请求列表
    '''
    def start_requests(self):
        # 抓取电影数据
        for type in self.typeList:
            for region in self.regionList:
                for year in self.yearList:
                    request = Request(self.first_url.format(classify=0, type=type, region=region, year=year), self.parse_pages)
                    request.meta['classify'] = 0
                    yield request

        # request = Request(self.first_url.format(classify=0, type=1, region=1, year=2010), self.parse_pages)
        # request.meta['classify'] = 0
        # yield request

        # 抓取电视剧数据
        for type in self.typeList:
            for region in self.regionList:
                for year in self.yearList:
                    request = Request(self.first_url.format(classify=1, type=type, region=region, year=year), self.parse_pages)
                    request.meta['classify'] = 1
                    yield request

        # request = Request(self.first_url.format(classify=1, type=1, region=3, year=2015), self.parse_pages)
        # request.meta['classify'] = 1
        # yield request

    '''
    处理每页内容
    '''
    def parse_pages(self, response):
        # print(response.text)
        classify = response.meta['classify']
        data = response.css('#content > div > div.article > div:nth-child(3)')
        if data.css('table'):
            list = data.css('table .nbg::attr(href)').extract()
            for url in list:
                full_url = self.base_url + url
                func = None
                if classify == 0: # 拉取电影
                    func = self.parse_movie_detail
                elif classify == 1: # 拉取电视剧
                    func = self.parse_teleplay_detail
                yield Request(full_url, func)


    '''
    处理电影详情页信息
    '''
    def parse_movie_detail(self, response):
        # print(response.text)
        item = MiaozMovieItem()
        self.process_response(response, item)
        yield item

        # 生成图片下载Request
        imageItem = ImageItem()
        image_urls = [item['logo_url']]
        imageItem['image_urls'] = image_urls
        yield imageItem

    '''
    处理电视剧详情页信息
    '''
    def parse_teleplay_detail(self, response):
        # print(response.text)
        item = MiaozTeleplayItem()
        self.process_response(response, item)
        yield item

        # 生成图片下载Request
        imageItem = ImageItem()
        image_urls = [item['logo_url']]
        imageItem['image_urls'] = image_urls
        yield imageItem

    '''
    提取response信息
    '''
    def process_response(self, response, item):
        item['name'] = response.css('#content > h1 > span:nth-child(1)::text').extract_first()
        item['year'] = response.css('#content > h1 > span.year::text').extract_first()[1:-1]
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
        item['playwright'] = playwriteStr
        # 提取演员信息
        actorList = response.css('#info > span.actor > span.attrs > a')
        actorStr = ''
        for actor in actorList:
            if actorStr == '':
                actorStr = actor.css('::text').extract_first()
            else:
                actorStr = actorStr + '、' + actor.css('::text').extract_first()
        item['actor'] = actorStr
        # 提取类型信息
        item['type_ids'] = response.css('#info > span[property="v:genre"]::text').extract_first()
        # 提取国家信息
        result = re.search('<span class="pl">制片国家/地区:</span>(.*?)<br>', response.text)
        if result:
            item['region_ids'] = result.group(1)
        else:
            item['region_ids'] = ''
        # 提取语言信息
        result = re.search('<span class="pl">语言:</span>(.*?)<br>', response.text)
        if result:
            item['language'] = result.group(1)
        else:
            item['language'] = ''
        # 提取上映日期
        result = re.search('<span class="pl">上映日期:</span> <span>(.*?)</span><br>', response.text)
        if result:
            item['release_date'] = result.group(1)
        else:
            item['release_date'] = ''
        # 提取片长
        result = re.search('<span class="pl">片长:</span> <span>(.*?)</span><br>', response.text)
        if result:
            item['length'] = result.group(1)
        else:
            item['length'] = ''
        # 提取英文名
        result = re.search('<span class="pl">又名:</span>(.*?)<br>', response.text)
        if result:
            item['en_name'] = result.group(1)
        else:
            item['en_name'] = ''
        # 提取剧情简介
        item['introduction'] = response.css('#link-report').extract_first()
        # 提取数据来源
        result = re.search('<p style="text-indent:2em">数据来源:(.*?)</p>', response.text)
        if result:
            item['source'] = result.group(1)
        else:
            item['source'] = ''
        # 提取源站影片ID
        result = re.search('/static/poster/s/(\d+).jpg', item['logo_url'])
        if result:
            item['station_movie_id'] = result.group(1)
        else:
            item['station_movie_id'] = ''

        # 提取下载链接
        downloadUrls = response.css('table > tr')
        urlList = []
        for downloadUrl in downloadUrls:
            urlList.append(downloadUrl.css('td:nth-child(1) > p::text').extract_first())
        item['download_urls'] = urlList

