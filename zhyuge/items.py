# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

'''
喵爪电影-MiaozMovieItem
'''
class MiaozMovieItem(scrapy.Item):
    # 片名
    name = scrapy.Field()
    # 类型列表
    type_ids = scrapy.Field()
    year = scrapy.Field()
    logo_url = scrapy.Field()
    score = scrapy.Field()
    director = scrapy.Field()
    playwright = scrapy.Field()
    actor = scrapy.Field()
    # 地区列表
    region_ids = scrapy.Field()
    language = scrapy.Field()
    release_date = scrapy.Field()
    length = scrapy.Field()
    en_name = scrapy.Field()
    introduction = scrapy.Field()
    # 暂无数据（在每个pipeline中设定）
    station_id = scrapy.Field()
    # 资源来源
    source = scrapy.Field()
    station_movie_id = scrapy.Field()
    # 下载链接URLS
    download_urls = scrapy.Field()
    # 影片类型 1 电影、2 电视剧
    type = scrapy.Field()


'''
图片下载
'''
class ImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_paths = scrapy.Field()
    # 图片实际保存路径
    real_url = scrapy.Field()
