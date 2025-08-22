import json
from kafka import KafkaConsumer


def test_kafka_consumer():
    """
    测试Kafka消费者，监听test主题
    """
    # Kafka消费者配置
    consumer = KafkaConsumer(
        'temp4_processed',  # 主题名称
        bootstrap_servers=['180.76.250.147:19092'],
        group_id='test_group',  # 消费者组I
    )

    print("开始监听Kafka主题 'test'...")
    print("连接到服务器: 180.76.250.147:19092")

    try:
        for message in consumer:
            print(f"收到消息:")
            print(f"  主题: {message.topic}")
            print(f"  分区: {message.partition}")
            print(f"  偏移量: {message.offset}")
            print(f"  Key: {message.key}")
            print(f"  Value: {message.value}")
            print("-" * 50)
    except KeyboardInterrupt:
        print("用户中断监听")
    except Exception as e:
        print(f"消费消息时出错: {e}")
    finally:
        consumer.close()


if __name__ == "__main__":
    test_kafka_consumer()
