# -*- coding: utf-8 -*-

"""
# @Time    : 2025/3/3 14:17
# @User  : Mabin
# @Description  :MongoDB数据库操作工具类（单例、连接池）
"""
from bson import ObjectId
from pymongo import MongoClient
from threading import Lock

from application.settings import MONGODB_DATABASES


class MongoDBManager:
    """
    MongoDB数据库管理类
    :author Mabin
    使用示例：
    test_model = MongoDBManager()
    test_result = test_model.db["information"].insert_one({
        "name": "测试",
        "desc": "🤣🤣"
    })
    """
    _instances = {}  # 存储不同URI的连接实例
    _lock = Lock()  # 线程安全锁

    def __new__(cls, connect_key="default"):
        """
        单例核心逻辑
        :author Mabin
        :param str connect_key:数据库连接标识
        """
        if connect_key not in cls._instances:
            # 不存在对应连接标识的实例
            with cls._lock:
                # 实例化
                instance = super().__new__(cls)

                # 初始化数据库连接
                instance._init_connection(connect_key=connect_key)

                # 存储
                cls._instances[connect_key] = instance

        # 返回实例
        return cls._instances[connect_key]

    def _init_connection(self, connect_key="default"):
        """
        初始化新连接(连接池)
        :author Mabin
        :param str connect_key:数据库连接标识
        :return:
        """
        # 获取数据库链接配置
        connect_config = MONGODB_DATABASES.get(connect_key, None)
        if not connect_config:
            raise Exception(f"创建MongoDB数据库连接时，未查询到数据库链接配置！{connect_key}")

        # 创建连接池（自动管理连接池）
        self.client = MongoClient(
            host=connect_config["host"],
            port=connect_config["port"],
            username=connect_config["user"],
            password=connect_config["password"],
            authSource=connect_config["auth_source"],
            directConnection=True,
            maxPoolSize=200,  # 最大连接数
            minPoolSize=10,  # 最小保持连接数
            connectTimeoutMS=3000,  # 连接超时(3秒)
            socketTimeoutMS=5000,  # 操作超时(5秒)
            serverSelectionTimeoutMS=3000,  # 服务器选择超时
            waitQueueTimeoutMS=2000  # 等待队列超时
        )
        self.db = self.client[connect_config["database"]]  # 切换至指定数据库


class MongoDBDataStream:
    mongodb_manager = MongoDBManager()

    def __init__(self, collection, batch_size, sort_key, historical_cursor_position):
        self.collection = collection
        self.batch_size = batch_size
        self.sort_key = sort_key
        self.historical_cursor_position = historical_cursor_position
        self.cursor_query = {
            sort_key: {"$gt": ObjectId(historical_cursor_position)}} if historical_cursor_position else {}

    def get_all(self, query=None):
        cursor = (self.mongodb_manager.db[self.collection]
                  .find(
            filter=(query or {}) | self.cursor_query
        )
                  .sort(self.sort_key, 1)
                  .batch_size(self.batch_size))
        for doc in cursor:
            yield doc


if __name__ == '__main__':
    test_model = MongoDBDataStream(collection='raw_information_list', batch_size=1000, sort_key='_id',
                                      historical_cursor_position='')
    for doc in test_model.get_all():
        print(doc)
