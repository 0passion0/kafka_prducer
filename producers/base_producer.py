from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from kafka import KafkaProducer

from config import PRODUCER_CONFIG
from logger import get_logger


class BaseKafkaProducer(ABC):
    """
    抽象基类，负责：
    1) 创建并维护一个全局 KafkaProducer 实例（所有子类共用，避免重复建连）。
    2) 定义子类必须实现的两个钩子：transform() 和 value_serialize()。
    3) 提供 send_message() 与 flush_and_close() 两个公共方法，子类可直接复用。
    """

    logger = get_logger("producer")

    def __init__(self, topic: str, producer_config: dict = None, debug: bool = False):
        """
        传入 topic 名称，后续 send_message() 均发到该 topic
        """
        self.topic = topic
        # 允许传入特定的生产者配置，如果未提供则使用默认配置
        config = producer_config or PRODUCER_CONFIG
        self.producer = KafkaProducer(**config)
        self.debug = debug

    # ---------------- 公共方法 ----------------
    def send_message(self,
                     message: Dict[str, Any],
                     key: Optional[str] = None) -> None:
        """
        真正发送单条消息的方法
        :param message: 经过 transform 后的 dict
        :param key:     可选的 Kafka 消息 key，用于分区路由；通常放业务主键
        """
        # 数据转换
        transform_message = self.transform(message)
        # 序列化成字节
        value = self.value_serialize(transform_message)

        # 异步发送到 Kafka，返回一个 Future 对象
        future = self.producer.send(
            self.topic,
            value=value,
            key=key.encode('utf-8') if key else None
        )

        if self.debug:
            # 同步阻塞 （不需要可注释）
            record_metadata = future.get(timeout=10)
            self.logger.info(f"[Kafka] 已发送消息：{record_metadata}")
            # 注意：这里并未调用 future.get() 同步等待结果，追求高吞吐
            # 如果想每条都同步确认，可改成 future.get(timeout=10)

    def flush_and_close(self, timeout: float = 30.0):
        """
        刷新并关闭生产者连接
        """
        self.producer.flush(timeout=timeout)
        self.producer.close()

    # ---------------- 抽象方法（子类必须实现） ----------------
    @abstractmethod
    def transform(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        把 MongoDB 文档转换成要发到 Kafka 的消息体。
        子类可按业务需求重写，例如：
            1. 只发送部分字段，减小消息体积
            2. 重命名字段，方便下游统一
            3. 增加计算字段，如 hash、标签
            4. 过滤敏感字段，如手机号
        返回值必须是可 JSON 序列化的 Python 基本类型
        """
        raise NotImplementedError

    @abstractmethod
    def value_serialize(self, message: Any) -> bytes:
        """
        把要发送的消息转换成字节流。
        子类可按业务需求重写，例如：
            1. 改用 Avro、Protobuf 等更高效格式
            2. 对数据加密
            3. 压缩（KafkaProducer 已做压缩，这里一般不用再做）
        注意：Kafka 的 value 必须是 bytes
        """
        raise NotImplementedError
