# Kafka Producer 数据同步项目

本项目是一个将多种数据源数据同步到 Kafka 的 Python 应用程序。它支持增量同步，能够从各种数据源中读取数据并将数据发送到指定的 Kafka 主题。目前支持 MongoDB 数据源，后续将扩展支持更多数据源。

## 项目概述

该项目主要用于将各种数据源中的数据实时同步到 Kafka 消息队列中，以便其他系统可以消费这些数据进行进一步处理。项目采用模块化设计，基于抽象基类构建，易于扩展和维护，可以方便地添加新的数据源支持。

## 功能特性

- **多数据源支持**：当前支持 MongoDB，易于扩展支持其他数据源
- **Kafka 数据发送**：将读取的数据发送到 Kafka 主题
- **增量同步**：支持基于特定字段的增量数据同步
- **连接池管理**：各种数据源和 Kafka 连接均采用连接池管理，提高性能
- **可扩展架构**：基于抽象基类的设计，易于扩展支持其他数据源
- **日志记录**：完善的日志记录机制，便于监控和调试

## 项目结构

```
kafka_producer/
├── config.py                 # 配置文件，包含各种数据源和 Kafka 配置
├── main.py                   # 主程序入口
├── logger.py                 # 日志和状态管理模块
├── README.md                 # 项目说明文档
├── models/
│   ├── __init__.py
│   └── mongodb_manager.py    # MongoDB 连接管理器（单例模式）
├── producers/
│   ├── __init__.py
│   ├── base_producer.py      # Kafka 生产者的抽象基类
│   └── mongodb_producer.py   # MongoDB 到 Kafka 的具体实现
└── cursors/
    └── mongodb.cursors       # 游标文件，用于记录同步状态
```

## 核心组件

### 数据源管理器
- MongoDB 管理器：单例模式设计，使用连接池管理 MongoDB 连接
- 易于扩展支持其他数据源管理器（如 MySQL、PostgreSQL 等）

### Kafka 生产者基类 (BaseKafkaProducer)
- 抽象基类，定义了 Kafka 生产者的基本框架
- 提供统一的消息发送接口
- 支持消息转换和序列化功能
- 子类只需实现特定的抽象方法即可支持新的数据源

### 具体数据源实现
- MongoDB 到 Kafka 同步器：继承自 BaseKafkaProducer，实现 MongoDB 数据同步逻辑
- 易于扩展实现其他数据源到 Kafka 的同步器

## 配置说明

### MongoDB 配置
```python
MONGODB_DATABASES = {
    "default": {
        "type": "mongodb",
        'user': 'admin',
        'password': '',
        'auth_source': 'admin',
        'host': '',
        'port': 27017,
        'database': 'tlg',
        "charset": "utf8mb4"
    },
}
```

### Kafka 配置
```python
PRODUCER_CONFIG = {
    "bootstrap_servers": [],
    "compression_type": "gzip",
    "retries": 5,
    "acks": 1,
    "batch_size": 16384,
    "linger_ms": 1000,
}
```

## 使用方法

1. 配置数据源和 Kafka 连接参数（在 [config.py](file:///e:/python/kafka_prducer/config.py) 文件中）
2. 运行主程序：
   ```bash
   python main.py
   ```

## 工作原理

1. 从状态文件中读取上次同步的位置信息
2. 查询数据源中自上次同步以来的新数据
3. 将查询到的数据逐条发送到 Kafka 主题
4. 更新状态文件，记录本次同步的位置信息

## 扩展性

项目采用面向对象设计，易于扩展支持其他数据源：

1. 创建新的数据源管理器（如需要）
2. 继承 [BaseKafkaProducer](file:///e:/python/kafka_prducer/producers/base_producer.py#L12-L57) 类实现新的数据源生产者
3. 实现 [transform()](file:///e:/python/kafka_prducer/producers/base_producer.py#L43-L57) 和 [value_serialize()](file:///e:/python/kafka_prducer/producers/base_producer.py#L59-L70) 抽象方法
4. 在 [main.py](file:///e:/python/kafka_prducer/main.py) 中调用新的生产者类

未来将支持更多数据源，如 MySQL、PostgreSQL、Oracle 等关系型数据库以及其他 NoSQL 数据库。