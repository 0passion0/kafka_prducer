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
- **切面化处理**：使用装饰器实现日志记录和性能监控等横切关注点
- **命令行接口**：通过命令行参数灵活配置同步任务
- **结构化数据模型**：使用 Pydantic 定义严格的数据结构模型，确保数据一致性
- **数据迁移功能**：支持将数据从一个源迁移到另一个源

## 缺点

- **数据必须有增量字段**
- **无法对修改数据进行更新（除非将update_time做增量）**
- **无法对删除数据进行更新（除非将update_time做增量）**
- **数据暂时只做基础数据结构如json,字符串等，如datatime等类型需要单独处理（影响性能）**

## 项目结构

```
kafka_producer/
├── run_producers.py           # 数据同步程序入口文件
├── run_migrate.py             # 数据迁移程序入口文件
├── README.md                 # 项目说明文档
├── requirements.txt          # 项目依赖
├── application/              # 应用核心代码目录
│   ├── config.py             # 基础配置
│   ├── settings.py           # 数据库和Kafka配置
│   ├── cursor_model/         # 游标管理模块
│   │   ├── __init__.py
│   │   ├── base_cursor.py    # 游标管理抽象基类
│   │   └── file_cursor.py   # 文件游标管理实现
│   ├── db/                   # 数据库连接管理
│   │   ├── __init__.py
│   │   ├── BaseMysqlModel.py # MySQL基础模型
│   │   ├── MongoDBManager.py # MongoDB连接管理器
│   │   ├── info/             # 信息数据库模型
│   │   └── nfsc/             # NFSC数据库模型
│   ├── migrate/              # 数据迁移模块
│   │   ├── __init__.py
│   │   └── migrate_to_nfsc.py# NFSC数据迁移实现
│   ├── models/               # 数据结构定义
│   │   ├── __init__.py
│   │   └── kafka_models/     # Kafka数据模型
│   │       ├── __init__.py
│   │       ├── base_data_structure.py          # 基础数据结构模型
│   │       └── information_data_structure.py   # 资讯类数据结构模型
│   ├── producers/            # Kafka生产者实现
│   │   ├── __init__.py
│   │   ├── base_producer.py                   # Kafka生产者的抽象基类
│   │   └── information_mongo_to_kafka_producer.py # 具体的MongoDB到Kafka同步实现
│   └── utils/                # 工具模块
│       ├── __init__.py
│       ├── decorators.py     # 装饰器模块，处理横切关注点
│       └── logger.py         # 日志模块
├── runtime/                  # 运行时数据目录
│   ├── cursors/              # 游标文件存储目录
│   └── log/                  # 日志文件目录
└── docker-compose/           # Docker Compose配置
    └── docker-compose.yml
```

## 核心组件

### 数据源管理器

- MongoDB 管理器：单例模式设计，使用连接池管理 MongoDB 连接
- MySQL 管理器：使用连接池管理 MySQL 连接
- 易于扩展支持其他数据源管理器（如 PostgreSQL 等）

### Kafka 生产者基类 (BaseKafkaProducer)

- 抽象基类，定义了 Kafka 生产者的基本框架
- 提供统一的消息发送接口
- 支持消息转换和序列化功能

### 装饰器模块 (decorators.py)

- 提供日志记录和性能监控等横切关注点的处理
- 通过注解方式应用，降低业务代码的侵入性

### 游标管理 (cursor_model)

- 抽象游标管理接口，支持多种游标存储方式
- 默认实现基于文件的游标管理

### 数据结构模型 (models/kafka_models)

- 基于 Pydantic 的数据结构模型，确保数据一致性和有效性
- 支持数据序列化为 JSON 格式
- 可扩展支持不同类型的数据结构

### 具体数据源实现

- MongoDB 到 Kafka 同步器：继承自 BaseKafkaProducer，实现 MongoDB 数据同步逻辑
- 易于扩展实现其他数据源到 Kafka 的同步器

### 数据迁移模块

- 支持将数据从一个源迁移到另一个源
- 基于基类和子类的层次结构设计，易于扩展

## 运行方式

项目有两种运行模式：数据同步和数据迁移。

### 数据同步

通过命令行参数进行配置和运行：

```bash
python run_producers.py --topic <kafka_topic> --data_type <data_type> [--full_amount True] [--debug True]
```

参数说明：
- `--topic`: Kafka主题名称（必填）
- `--data_type`: 数据类型（必填）
- `--full_amount`: 是否进行全量同步，默认为增量同步
- `--debug`: 是否开启调试模式，会打印详细日志

示例：
```bash
python run_producers.py --topic temp5 --data_type information --debug True
```

### 数据迁移

通过命令行参数指定迁移任务：

```bash
python run_migrate.py --task <task_name>
```

参数说明：
- `--task`: 迁移任务名称（必填）

示例：
```bash
python run_migrate.py --task nfsc_task
```

## 配置说明

### MongoDB 配置

在 [application/settings.py](file:///D:/company_project/kafka_prducer/kafka_prducer/application/settings.py) 文件中配置 MongoDB 连接信息：

```python
MONGODB_DATABASES = {
    "default": {
        "type": "mongodb",
        'user': '',
        'password': '',
        'auth_source': 'admin',  # 认证数据库（必须与用户创建库一致）
        'host': '192.168.1.245',
        'port': 27017,
        'database': 'raw_data_temp',
        "charset": "utf8mb4"
    },

}
```

### Kafka 配置

在 [application/settings.py](file:///D:/company_project/kafka_prducer/kafka_prducer/application/settings.py) 文件中配置 Kafka 连接信息：

```python
PRODUCER_CONFIG = {
    # Kafka 集群地址列表（ip:port）
    "bootstrap_servers": ['127.0.0.1:19092', '127.0.0.1:19096', '127.0.0.1:19100'],
    # 消息压缩方式
    "compression_type": "gzip",
    # 发送失败时的重试次数
    "retries": 5,
    # 多少个副本确认后才算发送成功：
    #   0：不等待确认（最快，可能丢数据）
    #   1：只等 leader 确认（折中）
    #   all/-1：等所有 ISR 副本确认（最安全，最慢）
    "acks": 1,
    # 一批消息的字节数阈值，达到该大小或超过 linger_ms 就立即发送
    "batch_size": 512 * 1024,  # 16 KB
    # 消息在客户端缓冲区最多等待多少毫秒再发送（与 batch_size 配合做微批）
    "linger_ms": 1000,
}
```