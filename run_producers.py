import argparse
import sys

from application.producers.information_mongo_to_kafka_producer import InformationtoKafkaProducer
from application.utils.decorators import log_execution, monitor_performance


@log_execution
@monitor_performance
def full_sync(topic, data_type, **kwargs):
    """
    同步数据到Kafka
    
    Args:
        topic (str): Kafka主题名称
        data_type (str): 数据类型，目前支持 'information'
        **kwargs: 其他参数
            full_amount (bool): 是否全量同步，默认False（增量同步）
            debug (bool): 是否开启调试模式，默认False
    
    Raises:
        ValueError: 当data_type不被支持时抛出异常
    """
    full_amount = kwargs.get('full_amount', False)
    debug = kwargs.get('debug', False)

    match data_type:
        case 'information':
            producer = InformationtoKafkaProducer(
                topic=topic, full_amount=full_amount, debug=debug
            )
            producer.sync()
        case _:
            raise ValueError(f'不支持的数据源：{topic}')


def main():
    sys.argv.extend([
        '--topic', 'temp4',
        '--data_type', 'information',
        '--full_amount', 'True',
        '--debug', 'True'
    ])
    parser = argparse.ArgumentParser(description='数据同步到Kafka工具')
    parser.add_argument('--topic', required=True, help='Kafka主题名称')
    parser.add_argument('--data_type', required=True, help='主题下的类型（默认全选）')
    parser.add_argument('--full_amount', help='是否全量同步（默认增量）')
    parser.add_argument('--debug', help='同步检查是否正常生产数据')

    args = parser.parse_args()

    # 构建参数字典
    kwargs = {}
    if args:
        kwargs['full_amount'] = args.full_amount
        kwargs['debug'] = args.debug

    # 执行同步
    full_sync(args.topic, args.data_type, **kwargs)


if __name__ == "__main__":
    "--data_source mongodb --topic temp4 --full_amount True --debug True"
    main()
