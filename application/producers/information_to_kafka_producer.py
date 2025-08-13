from typing import Dict, Any


from bson import ObjectId
from application.cursor_model import FileCursorManager
from application.db.mongodb_manager import MongoDBManager, MongoDBDataStream
from application.models.information_data_structure import InformationDataStructure
from application.producers.base_producer import BaseKafkaProducer


class InformationtoKafkaProducer(BaseKafkaProducer):
    mongodb_manager = MongoDBManager()
    collection = 'raw_information_list'
    sort_key = '_id'
    batch_size = 1000
    data_type = "informationto"

    def __init__(self,
                 topic: str,
                 full_amount: str = False,
                 debug: bool = False,
                 producer_config: dict = None):

        super().__init__(topic, producer_config, debug)

        self.cursor = FileCursorManager(collection=self.collection, topic=topic, full_amount=full_amount)  # 创建游标管理对象

        self.mongodb_stream = MongoDBDataStream(collection=self.collection, batch_size=self.batch_size,
                                                sort_key=self.sort_key,
                                                historical_cursor_position=self.cursor.load())

    # ---------- 实现父类抽象 ----------
    def transform(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        默认策略：把整个文档发出去，并把 _id 转成字符串方便下游消费。
        如想过滤字段、重命名、计算新字段，在此处修改即可。
        """
        # 确保 _id 是字符串格式
        if '_id' in doc and isinstance(doc['_id'], ObjectId):
            doc['uid'] = str(doc['_id'])
        if 'create_time' in doc:
            doc['create_time'] = str(doc['create_time'])

        return doc

    def value_serialize(self, message: Any) -> bytes:
        info = InformationDataStructure(
            topic=self.topic,
            data_type=self.data_type,

            uid=message.get('uid'),
            name=message.get('info_name', ''),
            created_at=message.get('create_time', ''),
            data={
                "info_date": message.get('info_date', ''),
                "info_section": message.get('info_section', ''),
                "info_author": message.get('info_author', ''),
                "info_source": message.get('info_source', ''),
            },
            metadata={
                "raw_html": message.get('raw_html'),
                "info_html": message.get('info_html'),
                "marc_code": message.get('marc_code'),
                "main_site": message.get('main_site'),
                "details_page": message.get('details_page', ''),
                "resource_label": message.get('resource_label', '') or '',
            },
            affiliated_data={
                "link_data": message.get('link_data', '') or [],
                "files": message.get('files', ''),
            }
        )
        return info.to_json()

    def sync(self, query=None):
        for doc in self.mongodb_stream.get_all(query=query):
            self.send_message(doc)
            self.mongodb_stream.historical_cursor_position = doc.get(self.sort_key)

    def __del__(self):
        self.cursor.save(self.mongodb_stream.historical_cursor_position)
