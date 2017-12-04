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
from zhyuge.items import MiaozMovieItem, ImageItem
from zhyuge.service.db_service import MovieTypeService, MovieService, RegionService, StationService, DownloadUrlService

'''
喵爪电影MySQL入库
'''
class MiaozMoviePipeline(object):

    station_name = '喵爪电影'

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
        station_entity = self.stationService.select_by_name(self.station_name)
        item['station_id'] = station_entity['station_id']

        # 电影/电视剧 数据入库（insertOrUpdate）
        movie_id = None
        params = {'station_id': item['station_id'], 'station_movie_id': item['station_movie_id']}
        result = self.movieService.select_by_station(params)
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
电影图片
'''
class ImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        # image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return request.meta['real_url']

    def get_media_requests(self, item, info):
        if not isinstance(item, ImageItem):
            return item

        for image_url in item['image_urls']:
            request = Request(image_url)
            request.meta['classify'] = 2
            request.meta['real_url'] = item['real_url']
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
