import argparse
from cursor_model.mongo_cursor import FileCursorManager
from producers.mongodb_producer import MongoDBtoKafka

from decorators import log_execution


@log_execution
def full_sync(data_source, topic, key, **kwargs):
    """
    执行指定数据源到Kafka的全量同步

    :param data_source: 数据源类型
    :param topic: Kafka主题名称
    :param key: 用于分区的键字段名
    :param kwargs: 其他参数
    """

    # 根据数据源类型选择相应的游标管理器和生产者
    if data_source == 'mongodb':
        collection = kwargs.get('collection', 'collection')
        
        cursor_manager = FileCursorManager()
        producer = MongoDBtoKafka(
            topic=topic, collection=collection, key=key)

        # 从状态存储中加载上次同步的时间戳
        last_seen = cursor_manager.load()

        # 执行同步操作并获取本次同步的最大时间戳
        max_id = producer.sync(last_seen)

        # 保存本次同步的最大时间戳到状态存储
        cursor_manager.save(max_id)
    else:
        raise ValueError(f"不支持的数据源类型: {data_source}")


def main():
    parser = argparse.ArgumentParser(description='数据同步到Kafka工具')
    parser.add_argument('--data_source', required=True, help='数据源类型 (如: mongodb)')
    parser.add_argument('--topic', required=True, help='Kafka主题名称')
    parser.add_argument('--key', required=True, help='用于分区的键字段名')
    parser.add_argument('--collection', help='MongoDB集合名称 (仅mongodb数据源需要)')

    args = parser.parse_args()

    # 构建参数字典
    kwargs = {}
    if args.collection:
        kwargs['collection'] = args.collection

    # 执行同步
    full_sync(args.data_source, args.topic, args.key, **kwargs)


if __name__ == "__main__":
    main()