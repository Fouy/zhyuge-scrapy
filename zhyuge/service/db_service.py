import logging

from zhyuge.service.dbhelper import DBTemplete

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
章鱼哥电影
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

'''
movie数据库操作
'''
class MovieService():

    logger = logging.getLogger()

    def __init__(self):
        self.conn = DBTemplete().connectDB()

    '''
    插入操作
    '''
    def insert(self, item):
        cursor = self.conn.cursor()
        try:
            sql = 'insert into `movie` ( `status`, `en_name`, `language`, `create_time`, `actor`, `playwright`, `type_ids`, `score`, `logo_url`,' \
                  ' `region_ids`, `year`, `name`, `length`, `release_date`, `modify_time`, `director`, `station_id`, `introduction`, `source`, `station_movie_id`, `type`, `station_url`) ' \
                  + "values ( '1', %s, %s, NOW(), %s, %s, %s, %s, %s," \
                    " %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s)"
            params = (
                item["en_name"], item["language"], item["actor"], item["playwright"], item["type_ids"], item["score"], item["logo_url"],
                item["region_ids"], item["year"], item["name"], item["length"], item["release_date"], item["director"],
                item["station_id"], item["introduction"], item["source"], item["station_movie_id"], item["type"], item["station_url"])
            cursor.execute(sql, params)
            self.conn.commit()

            return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            self.logger.error('插入movie失败', e)

    '''
    更新操作
    '''
    def update_by_station(self, item):
        cursor = self.conn.cursor()
        try:
            sql = "update `movie` set `source`=%s, `en_name`=%s, `language`=%s, `actor`=%s, `playwright`=%s, " \
                  "`score`=%s, `logo_url`=%s, `region_ids`=%s, `year`=%s, `name`=%s, `length`=%s, `release_date`=%s, " \
                  "`type_ids`=%s, `director`=%s, `introduction`=%s, `modify_time`=NOW() " \
                  "where `station_id`='1' and `station_movie_id`='9999' "
            params = (item["source"], item["en_name"], item["language"], item["actor"], item["playwright"],
                item["score"], item["logo_url"], item["region_ids"], item["year"], item["name"], item["length"], item["release_date"],
                item["type_ids"], item["director"], item["introduction"])
            cursor.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.logger.error('更新movie信息失败', e)


    '''
    根据station信息查询实体
    item = { 'station_id : 1, 'station_movie_id' : 2}
    '''
    def select_by_station(self, item):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `movie` where station_id = %s and station_movie_id = %s '
            params = (item['station_id'], item['station_movie_id'])
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except Exception as e:
            self.logger.error('根据station信息查询movie实体失败', e)


'''
movie_type数据库操作
'''
class MovieTypeService(object):

    def __init__(self):
        self.conn = DBTemplete().connectDB()

    '''
    插入操作
    '''
    def insert(self, item):
        cursor = self.conn.cursor()
        try:
            sql = 'insert into `movie_type` (`name`) values ( %s )'
            params = (item["name"])
            cursor.execute(sql, params)
            self.conn.commit()

            return cursor.lastrowid
        except:
            self.conn.rollback()
            print('插入movie_type失败')

    '''
    根据type_id查询实体
    '''
    def select_by_id(self, type_id):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `movie_type` where type_id = %s '
            params = (type_id)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except:
            print('查询movie_type失败')

    '''
    根据name查询实体
    '''
    def select_by_name(self, name):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `movie_type` where name = %s '
            params = (name)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except:
            print('查询movie_type失败')


'''
region数据库操作
'''
class RegionService():

    def __init__(self):
        self.conn = DBTemplete().connectDB()

    '''
    插入操作
    '''
    def insert(self, item):
        cursor = self.conn.cursor()
        try:
            sql = 'insert into `region` ( `name`) ' + "values ( %s )"
            params = (item["name"])
            cursor.execute(sql, params)
            self.conn.commit()

            return cursor.lastrowid
        except:
            self.conn.rollback()
            print('插入region失败')

    '''
    根据region_id查询实体
    '''
    def select_by_id(self, region_id):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `region` where region_id = %s '
            params = (region_id)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except:
            print('根据region_id查询region失败')

    '''
    根据name查询实体
    '''
    def select_by_name(self, name):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `region` where name = %s '
            params = (name)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except:
            print('根据name查询region失败')


'''
station数据库操作
'''
class StationService():

    def __init__(self):
        self.conn = DBTemplete().connectDB()

    '''
    插入操作
    '''
    def insert(self, item):
        cursor = self.conn.cursor()
        try:
            sql = "insert into `station` ( `home_url`, `name`, `type`) values ( %s, %s, %s)"
            params = (item["home_url"], item["name"], item["type"])
            cursor.execute(sql, params)
            self.conn.commit()

            return cursor.lastrowid
        except:
            self.conn.rollback()
            print('插入station失败')

    '''
    根据station_id查询实体
    '''
    def select_by_id(self, station_id):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `station` where station_id = %s '
            params = (station_id)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except:
            print('根据station_id查询失败')

    '''
    根据name查询实体
    '''
    def select_by_name(self, name):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `station` where name = %s '
            params = (name)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except:
            print('根据name查询失败')


'''
download_url数据库操作
'''
class DownloadUrlService():

    logger = logging.getLogger()

    def __init__(self):
        self.conn = DBTemplete().connectDB()

    '''
    批量插入操作
    '''
    def batch_insert(self, list):
        cursor = self.conn.cursor()
        try:
            for item in list:
                sql = "insert into `download_url` ( `modify_time`, `type`, `order`, `movie_id`, `create_time`, `url`) " \
                      "values ( NOW(), %s, %s, %s, NOW(), %s);"
                params = (item["type"], item["order"], item["movie_id"], item["url"])
                cursor.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.logger.error('download_url批量插入操作失败', e)

    '''
    根据movie_id删除
    '''
    def delete_by_movie(self, movie_id, type):
        cursor = self.conn.cursor()
        try:
            sql = 'delete from `download_url` where movie_id = %s and type = %s '
            params = (movie_id, type)
            cursor.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.logger.error('根据movie_id, type删除download_url失败', e)




'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
章鱼哥图片
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


'''
picture数据库操作
'''
class PictureService():

    logger = logging.getLogger()

    def __init__(self):
        self.conn = DBTemplete().connectDB()

    '''
    插入操作
    '''
    def insert(self, item):
        cursor = self.conn.cursor()
        try:
            sql = 'insert into `picture` ( `station_pic_id`, `source`, `status`, `type_id`, `modify_time`, `logo_url`, ' \
                  '`station_id`, `create_time`, `name`, `station_url`) ' \
                  'values ( %s, %s, "1", %s, NOW(), %s, %s, NOW(), %s, %s)'

            params = (
                item["station_pic_id"], item["source"], item["type_id"], item["logo_url"],
                item["station_id"], item["name"], item["station_url"])
            cursor.execute(sql, params)
            self.conn.commit()

            return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            self.logger.error('插入picture失败', e)

    '''
    根据station信息查询实体
    item = { 'station_id : 1, 'station_pic_id' : 2}
    '''
    def select_by_station(self, item):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `picture` where station_id = %s and station_pic_id = %s '
            params = (item['station_id'], item['station_pic_id'])
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except Exception as e:
            self.logger.error('根据station信息查询picture实体失败', e)


'''
picture_type数据库操作
'''
class PictureTypeService(object):

    def __init__(self):
        self.conn = DBTemplete().connectDB()

    '''
    插入操作
    '''
    def insert(self, item):
        cursor = self.conn.cursor()
        try:
            sql = 'insert into `picture_type` (`name`) values ( %s )'
            params = (item["name"])
            cursor.execute(sql, params)
            self.conn.commit()

            return cursor.lastrowid
        except:
            self.conn.rollback()
            print('插入picture_type失败')

    '''
    根据type_id查询实体
    '''
    def select_by_id(self, type_id):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `picture_type` where type_id = %s '
            params = (type_id)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except:
            print('查询picture_type失败')

    '''
    根据name查询实体
    '''
    def select_by_name(self, name):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `picture_type` where name = %s '
            params = (name)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except:
            print('查询picture_type失败')

'''
picture_url数据库操作
'''
class PictureUrlService():

    logger = logging.getLogger()

    def __init__(self):
        self.conn = DBTemplete().connectDB()

    '''
    批量插入操作
    '''
    def batch_insert(self, list):
        cursor = self.conn.cursor()
        try:
            # 检查是否已经存储URL, 已存储则直接返回
            result = self.select_by_url(list[0]['url'])
            if result:
                return

            for item in list:
                sql = "insert into `picture_url` ( `modify_time`, `order`, `picture_id`, `create_time`, `url`) " \
                      "values ( NOW(), %s, %s, NOW(), %s);"
                params = (item["order"], item["picture_id"], item["url"])
                cursor.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.logger.error('picture_url批量插入操作失败', e)

    '''
    根据URL查询实体
    '''
    def select_by_url(self, url):
        cursor = self.conn.cursor()
        try:
            sql = 'select * from `picture_url` where url = %s '
            params = (url)
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        except Exception as e:
            self.logger.error('查询picture_url失败', e)
