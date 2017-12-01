
from enum import IntEnum, unique

'''
爬虫相关常量
'''

'''
爬取数据分类类型
'''
@unique
class ClassifyEnum(IntEnum):
    Movie = 0
    Teleplay = 1
    Image = 2
    Game = 3

    @classmethod
    def get_enum(cls, value):
        for name, member in ClassifyEnum.__members__.items():
            if value == member.value:
                return cls(value)
        return None


# if __name__ == '__main__':
#     print(ClassifyEnum.get_enum(0).value)