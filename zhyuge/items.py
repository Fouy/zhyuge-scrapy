# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
章鱼哥电影
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

'''
电影-MovieItem
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
    station_url = scrapy.Field()


'''
图片下载
'''
class ImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_paths = scrapy.Field()
    # 图片实际保存路径
    real_url = scrapy.Field()
    # 缩略图实际保存路径
    thumb_url = scrapy.Field()




'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
章鱼哥图片
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


'''
图片-PictureItem
'''
class PictureItem(scrapy.Item):
    # 图片标题
    name = scrapy.Field()
    # 类型ID
    type_id = scrapy.Field()
    type_name = scrapy.Field()
    logo_url = scrapy.Field()
    # 资源来源
    source = scrapy.Field()
    # 暂无数据（在每个pipeline中设定）
    station_id = scrapy.Field()
    station_pic_id = scrapy.Field()
    station_url = scrapy.Field()

    # 下载链接URLS
    picture_urls = scrapy.Field()

'''
图片下载
'''
class PictureUrlItem(scrapy.Item):
    picture_id = scrapy.Field()
    url = scrapy.Field()
    order = scrapy.Field()


