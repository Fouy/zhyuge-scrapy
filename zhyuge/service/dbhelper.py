import pymysql
from scrapy.utils.project import get_project_settings  # 导入seetings配置
from twisted.enterprise import adbapi


class DBTemplete(object):

    def __init__(self):
        self.settings = get_project_settings()  # 获取settings配置

        self.host = self.settings['MYSQL_HOST']
        self.port = self.settings['MYSQL_PORT']
        self.user = self.settings['MYSQL_USER']
        self.passwd = self.settings['MYSQL_PASSWD']
        self.db = self.settings['MYSQL_DBNAME']

    # 连接到具体的数据库
    def connectDB(self):
        conn = pymysql.connect(host = self.host,
                               port = self.port,
                               user = self.user,
                               passwd = self.passwd,
                               db = self.db,
                               charset = 'utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        return conn



# class DBTemplete(object):
#
#     __instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if cls.__instance is None:
#             cls.__instance = super().__new__(cls)
#             cls.__instance = object.__new__(cls)
#             cls.__instance = super(DBTemplete, cls).__new__(cls)
#             print(')))))))))))))))))))))')
#         return cls.__instance
#
#     def __init__(self):
#         if self.__instance:
#             pass
#
#         settings = get_project_settings()  # 获取settings配置，设置需要的信息
#
#         dbparams = dict(
#             host=settings['MYSQL_HOST'],
#             db=settings['MYSQL_DBNAME'],
#             user=settings['MYSQL_USER'],
#             passwd=settings['MYSQL_PASSWD'],
#             charset='utf8',
#             cursorclass=pymysql.cursors.DictCursor,
#             use_unicode=False,
#         )
#         self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy...
#         print(settings['MYSQL_HOST'] + '--------------------')

