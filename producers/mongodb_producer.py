import json
import time
from typing import Dict, Any

from models.mongodb_manager import MongoDBManager
from producers.base_producer import BaseKafkaProducer

from pymongo.cursor import Cursor
from bson import ObjectId


class MongoDBtoKafka(BaseKafkaProducer):
    """
    具体实现类，负责把 MongoDB 某个集合同步到 Kafka
    """

    # 封装好的 Mongo 连接管理器（内部做了连接池）
    mongodb_manager = MongoDBManager()

    def __init__(self,
                 topic: str,
                 collection: str,
                 key: str = None,
                 batch_size: int = 1000,
                 producer_config: dict = None):
        """
        初始化MongoDB到Kafka的生产者实例

        :param topic: Kafka主题名称，数据将发送到该主题
        :param collection: MongoDB集合名称，将从该集合读取数据
        :param key: 用于分区的键字段名，如果指定，将使用该字段值作为Kafka消息的key
        :param batch_size: 批处理大小，控制MongoDB每次网络往返批量拉取的文档数量
        :param producer_config: Kafka生产者配置，可选
        """

        super().__init__(topic, producer_config)
        self.collection = collection
        self.batch_size = batch_size
        self.key = key

    # ---------- 实现父类抽象 ----------
    def transform(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        默认策略：把整个文档发出去，并把 _id 转成字符串方便下游消费。
        如想过滤字段、重命名、计算新字段，在此处修改即可。
        """
        # 确保 _id 是字符串格式
        if '_id' in doc and isinstance(doc['_id'], ObjectId):
            doc['_id'] = str(doc['_id'])
        return doc

    def value_serialize(self, message: Any) -> bytes:
        """
        默认：把 dict → JSON → UTF-8 bytes
        如果想用 Avro，可换成 avro.serialize(message)
        """
        return json.dumps(message, ensure_ascii=False).encode("utf-8")

    def sync(self, last_max_id: str, query=None) -> str:
        """
        执行MongoDB到Kafka的数据同步操作

        该方法从MongoDB集合中读取大于指定ID的文档，并将它们发送到Kafka主题。
        同时会跟踪处理过的最大ID，用于下次增量同步。

        :param last_max_id: 上次同步的最大文档ID，本次同步将处理大于此ID的文档
        :param query: 额外的查询条件，用于过滤需要同步的文档
        :return: 本次同步处理过的最大文档ID
        """

        # 构建查询条件并获取游标
        cursor: Cursor = (
            self.mongodb_manager.db[self.collection]
            .find(
                filter=(query or {}) | {"_id": {"$gt": ObjectId(last_max_id)}},
            )
            .sort("_id", 1)
            .batch_size(self.batch_size)
        )

        max_create_id = last_max_id  # 记录本次最大ID

        # 遍历游标中的每个文档并发送到Kafka
        for doc in cursor:
            doc.pop('create_time', None)  # 移除create_time字段
            max_create_id = doc.pop('_id')  # 获取并移除文档ID
            self.send_message(doc, key=self.key)  # 发送处理后的文档到Kafka

        self.logger.info(f"同步完成，本次同步最大 _id：{max_create_id}")
        return str(max_create_id)