from __future__ import annotations

from producers.mongodb_producer import MongoDBtoKafka
from logger import StateRepository


def full_sync():
    """
    执行MongoDB到Kafka的全量同步

    该函数从状态存储中加载上次同步的时间戳，然后从MongoDB集合中同步
    自该时间戳以来的所有数据到Kafka主题，最后保存本次同步的最大时间戳。
    """

    state_repo = StateRepository()
    mongo_repo = MongoDBtoKafka(
        topic="temp3", collection="collection", key="my_hash")

    # 从状态存储中加载上次同步的时间戳
    last_seen = state_repo.load()

    # 执行同步操作并获取本次同步的最大时间戳
    max_id = mongo_repo.sync(last_seen)

    # 保存本次同步的最大时间戳到状态存储
    state_repo.save(max_id)


if __name__ == "__main__":
    full_sync()
