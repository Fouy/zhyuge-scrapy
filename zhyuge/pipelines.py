# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib

import pymongo
import pymysql
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.utils.python import to_bytes
from twisted.enterprise import adbapi

from zhyuge.common.constants import ClassifyEnum
from zhyuge.items import MiaozMovieItem, ImageItem, PictureItem
from zhyuge.service.db_service import MovieTypeService, MovieService, RegionService, StationService, DownloadUrlService, \
    PictureService, PictureTypeService, PictureUrlService

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
章鱼哥电影
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

'''
电影/电视剧MySQL入库
'''
class MiaozMoviePipeline(object):

    # station_name = '喵爪电影'

    def __init__(self):
        self.movieService = MovieService()
        self.movieTypeService = MovieTypeService()
        self.regionService = RegionService()
        self.stationService = StationService()
        self.downloadUrlService = DownloadUrlService()

    '''
    pipeline默认调用
    '''
    def process_item(self, item, spider):
        if not isinstance(item, MiaozMovieItem):
            return item
        # urls为空时，舍弃影片
        if not item['download_urls']:
            return

        # 处理类型信息
        if item['type_ids']:
            item['type_ids'] = self.process_type_names(item['type_ids'])
        # 处理地区信息
        if item['region_ids']:
            item['region_ids'] = self.process_region_name(item['region_ids'])
        # 处理站点信息
        if item['source']:
            station_entity = self.stationService.select_by_name(item['source'])
            item['station_id'] = station_entity['station_id']

        # 电影/电视剧 数据入库（insertOrUpdate）
        movie_id = None
        params = {'station_id': item['station_id'], 'station_movie_id': item['station_movie_id']}
        result = self.movieService.select_by_station(params)
        if item['type'] == 2: # 电视剧
            if len(item['download_urls']) > 0:
                item['length'] = len(item['download_urls'])
        if not result:
            movie_id = self.movieService.insert(item)

        # 下载链接入库
        type = item['type']
        if movie_id and item['download_urls']:
            urls = []
            for index, url in enumerate(item['download_urls']):
                temp_url = { 'type':type, 'order':index+1, 'movie_id':movie_id, 'url':url }
                urls.append(temp_url)

            self.downloadUrlService.delete_by_movie(movie_id, type)
            self.downloadUrlService.batch_insert(urls)

        return item

    '''
    处理地区信息：如：美国/中国 --> 1,2
    如库中无文字匹配，则插入 地区信息
    '''
    def process_region_name(self, region_names):
        result = ''
        region_name_list = region_names.split('/')
        for region_name in region_name_list:
            region_name = region_name.strip()
            entity = self.regionService.select_by_name(region_name)
            # 无数据则新增一条
            if not entity:
                item = {'name':region_name}
                self.regionService.insert(item)
                entity = self.regionService.select_by_name(region_name)

            if result == '':
                result = str(entity['region_id'])
            else:
                result = result + ',' + str(entity['region_id'])
        return result

    '''
    处理电影类型：如：喜剧,剧情 --> 1,2
    如库中无文字匹配，则插入类型数据
    '''
    def process_type_names(self, type_names):
        result = ''
        type_name_list = type_names.split(',')
        for type_name in type_name_list:
            type_name = type_name.strip()
            entity = self.movieTypeService.select_by_name(type_name)
            # 无数据则新增一条
            if not entity:
                item = {'name' : type_name}
                self.movieTypeService.insert(item)
                entity = self.movieTypeService.select_by_name(type_name)

            if result == '':
                result = str(entity['type_id'])
            else:
                result = result + ',' + str(entity['type_id'])
        return result


'''
图片下载
'''
class ImagesPipeline(ImagesPipeline):

    # 重写下载地址
    def file_path(self, request, response=None, info=None):
        # image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return request.meta['real_url']

    # 重写缩略图地址
    def thumb_path(self, request, thumb_id, response=None, info=None):
        return request.meta['thumb_url']

    def get_media_requests(self, item, info):
        if not isinstance(item, ImageItem):
            return item

        for image_url in item['image_urls']:
            request = Request(image_url)
            request.meta['classify'] = 2    # 表示图片下载类型
            request.meta['real_url'] = item['real_url']
            request.meta['thumb_url'] = item['thumb_url']
            yield request


    def item_completed(self, results, item, info):
        if not isinstance(item, ImageItem):
            return item

        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item


'''
MongoDB入库Demo
'''
class ZhyugePipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db['movie'].update({'station_movie_id': item['station_movie_id']}, {'$set' : item}, True)
        return item




'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
章鱼哥图片
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

'''
图片MySQL入库
'''
class PicturePipeline(object):

    # station_name = '169美女'

    def __init__(self):
        self.pictureService = PictureService()
        self.pictureTypeService = PictureTypeService()
        self.stationService = StationService()
        self.pictureUrlService = PictureUrlService()

    '''
    pipeline默认调用
    '''
    def process_item(self, item, spider):
        if not isinstance(item, PictureItem):
            return item
        # urls为空时，舍弃
        if not item['picture_urls']:
            return
        # 处理url信息若logo_url为空，则默认第一张图片
        if item['logo_url'] == '':
            item['logo_url'] = item['picture_urls'][0]['url']

        # 处理站点信息
        if item['source']:
            station_entity = self.stationService.select_by_name(item['source'])
            item['station_id'] = station_entity['station_id']
        # 处理类型信息（type_id）
        if item['type_name']:
            # print(item['type_name'])
            type_entity = self.pictureTypeService.select_by_name(item['type_name'])
            item['type_id'] = type_entity['type_id']

        # 图片 数据入库（insertOrUpdate）
        params = {'station_id': item['station_id'], 'station_pic_id': item['station_pic_id']}
        result = self.pictureService.select_by_station(params)
        if not result:
            picture_id = self.pictureService.insert(item)
        else:
            picture_id = result['picture_id']

        # URL入库
        if item['picture_urls']:
            for index, url in enumerate(item['picture_urls']):
                url['picture_id'] = picture_id

            self.pictureUrlService.batch_insert(item['picture_urls'])

        return item


