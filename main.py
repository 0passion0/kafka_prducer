import argparse
import sys

from cursor_model.mongo_cursor import FileCursorManager
from producers.mongodb_producer import MongoDBtoKafka

from decorators import log_execution, monitor_performance


@log_execution
@monitor_performance
def full_sync(data_source, topic, key, **kwargs):
    """
    执行指定数据源到Kafka的全量同步

    :param data_source: 数据源类型
    :param topic: Kafka主题名称
    :param key: 用于分区的键字段名
    :param kwargs: 其他参数
    """

    match data_source:
        case 'mongodb':
            collection = kwargs.get('collection', 'collection')
            full_amount = kwargs.get('full_amount', False)
            debug = kwargs.get('debug', False)

            cursor_manager = FileCursorManager(collection, topic, key)  # 创建游标管理对象
            producer = MongoDBtoKafka(
                topic=topic, collection=collection, key=key, debug=debug)

            # 从状态存储中加载上次同步的时间戳
            load_max_id = cursor_manager.load(full_amount)

            # 执行同步操作并获取本次同步的最大时间戳
            max_id = producer.sync(load_max_id)

            # 保存本次同步的最大时间戳到状态存储
            cursor_manager.save(max_id)
        case _:
            ValueError(f"Invalid data source: {data_source}")


def main():
    sys.argv.extend([
        '--data_source', 'mongodb',
        '--topic', 'temp4',
        '--key', 'my_hash',
        '--collection', 'book',
        '--full_amount', 'True',
        # '--debug', 'True'
    ])
    parser = argparse.ArgumentParser(description='数据同步到Kafka工具')
    parser.add_argument('--data_source', required=True, help='数据源类型 (如: mongodb)')
    parser.add_argument('--topic', required=True, help='Kafka主题名称')
    parser.add_argument('--key', required=True, help='用于分区的键字段名')
    parser.add_argument('--collection', help='MongoDB集合名称 (仅mongodb数据源需要)')
    parser.add_argument('--full_amount', help='是否全量同步（默认增量）')
    parser.add_argument('--debug', help='同步检查是否正常生产数据')

    args = parser.parse_args()

    # 构建参数字典
    kwargs = {}
    if args.collection:
        kwargs['collection'] = args.collection
        kwargs['full_amount'] = args.full_amount
        kwargs['debug'] = args.debug

    # 执行同步
    full_sync(args.data_source, args.topic, args.key, **kwargs)


if __name__ == "__main__":
    "--data_source mongodb --topic temp4 --key my_hash --collection book --full_amount True --debug True"
    main()
