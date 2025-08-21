import json
from typing import Dict, Any
from bson import ObjectId

from application.cursor_model.file_cursor import FileCursorManager
from application.db.mongodb_manager import MongoDBManager, MongoDBDataStream
from application.models.kafka_models.information_data_structure import InformationDataStructure
from application.producers.base_producer import BaseKafkaProducer


class InformationtoKafkaProducer(BaseKafkaProducer):
    """
    Kafka 生产者：将 MongoDB 中的 `raw_information_list` 数据发送到 Kafka

    :ivar mongodb_manager: MongoDB 管理实例
    :ivar collection: MongoDB 集合名
    :ivar sort_key: 排序键（通常用于增量同步）
    :ivar batch_size: 批量读取大小
    :ivar data_type: 数据类型标识
    """
    mongodb_manager = MongoDBManager()
    collection = 'raw_information_list'
    sort_key = '_id'
    batch_size = 1000
    data_type = "informationto"

    def __init__(self,
                 topic: str,
                 full_amount: bool = False,
                 debug: bool = False,
                 producer_config: dict = None):
        """
        初始化生产者

        :param topic: Kafka 主题名
        :param full_amount: 是否全量同步，True 表示从头开始
        :param debug: 调试模式
        :param producer_config: Kafka 生产者配置
        """
        super().__init__(topic, producer_config, debug)

        # 创建游标管理器（用于记录增量同步位置）
        self.cursor = FileCursorManager(
            collection=self.collection,
            topic=topic,
            full_amount=full_amount
        )

        # 创建 MongoDB 数据流管理器
        self.mongodb_stream = MongoDBDataStream(
            collection=self.collection,
            batch_size=self.batch_size,
            sort_key=self.sort_key,
            historical_cursor_position=self.cursor.load()  # 加载历史游标位置
        )

    def sync(self, query: Dict[str, Any] = None) -> None:
        """
        同步数据：从 MongoDB 按批读取并发送到 Kafka

        :param query: MongoDB 查询条件
        """
        for doc in self.mongodb_stream.get_all(query=query):
            self.send_message(doc)
            # 更新游标位置
            self.mongodb_stream.historical_cursor_position = doc.get(self.sort_key)

    # ---------- 实现父类抽象方法 ----------
    def transform(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        数据转换逻辑：将 MongoDB 文档转换为适合下游消费的格式

        :param doc: MongoDB 文档
        :return: 转换后的文档字典
        """
        # 确保 _id 转换为字符串，避免下游解析 ObjectId 出错
        if '_id' in doc and isinstance(doc['_id'], ObjectId):
            doc['uid'] = str(doc['_id'])

        # 确保 create_time 为字符串格式（避免 datetime 类型在 JSON 序列化时报错）
        if 'create_time' in doc and doc['create_time'] is not None:
            doc['create_time'] = str(doc['create_time'])

        return doc

    def value_serialize(self, message: Dict[str, Any]) -> bytes:
        """
        将消息数据结构化并序列化为 JSON 字节流

        :param message: 原始消息字典
        :return: JSON 格式字节流
        """
        # 创建结构化信息对象
        info = InformationDataStructure(
            topic=self.topic,
            data_type=self.data_type,
            uid=message.get('uid'),
            name=message.get('info_name', ''),
            created_at=message.get('create_time', ''),
            tag_code=message.get('tag_code', ''),
            tag_values=json.dumps(message.get('column_info', [])),

            data={
                "info_date": message.get('info_date', ''),
                # "info_section": message.get('info_section', ''),
                "info_author": message.get('info_author', ''),
                "info_source": message.get('info_source', ''),
                'description': message.get('description', ''),
            },
            metadata={
                "marc_code": message.get('marc_code'),
                "main_site": message.get('main_site'),
                "details_page": message.get('details_page', ''),
            },
            affiliated_data={
                "link_data": message.get('link_data') or [],
                "files": message.get('files', ''),
            }
        )
        return info.to_json()

    def __del__(self):
        """
        析构方法：保存当前游标位置，保证下次同步时可从断点续传
        """
        self.cursor.save(self.mongodb_stream.historical_cursor_position)
