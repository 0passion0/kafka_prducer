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
- **数据暂时只做基础数据结构如json,字符串等，如datetime等类型需要单独处理（影响性能）**

## 项目结构

```
kafka_producer/
├── run_producers.py              # 数据同步程序入口文件
├── run_migrate.py                # 数据迁移程序入口文件
├── README.md                     # 项目说明文档
├── requirements.txt              # 项目依赖
├── application/                  # 应用核心代码目录
│   ├── config.py                 # 基础配置
│   ├── settings.py               # 数据库和Kafka配置
│   ├── cursor_model/             # 游标管理模块
│   │   ├── __init__.py
│   │   ├── base_cursor.py        # 游标管理抽象基类
│   │   └── file_cursor.py        # 文件游标管理实现
│   ├── db/                       # 数据库连接管理
│   │   ├── __init__.py
│   │   ├── elastic_db/           # ElasticSearch数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── base_elastic.py
│   │   │   └── base_elastic_aggregate.py
│   │   ├── mongo_db/             # MongoDB数据库相关
│   │   │   ├── __init__.py
│   │   │   └── mongo_db_manager.py
│   │   └── mysql_db/             # MySQL数据库相关
│   │       ├── __init__.py
│   │       ├── base_mysql_model.py
│   │       ├── info/
│   │       │   ├── ResourceInformationAttachmentList.py
│   │       │   ├── ResourceInformationList.py
│   │       │   ├── ResourceInformationSectionList.py
│   │       │   ├── ResourceInformationTagsRelation.py
│   │       │   ├── ResourceSourceDict.py
│   │       │   └── __init__.py
│   │       └── nsfc/
│   │           ├── NsfcInfoList.py
│   │           ├── NsfcInfoSectionList.py
│   │           ├── NsfcInfoTypeDict.py
│   │           ├── NsfcPublishProjectCodeDict.py
│   │           ├── NsfcResourceSourceDict.py
│   │           └── __init__.py
│   ├── migrate/                  # 数据迁移模块
│   │   ├── __init__.py
│   │   ├── info_to_nfsc.py       # 资源信息到国自然基金数据迁移实现
│   │   └── nfsc_to_es.py         # 国自然基金到ES数据迁移实现
│   ├── models/                   # 数据结构定义
│   │   ├── __init__.py
│   │   └── kafka_models/         # Kafka数据模型
│   │       ├── __init__.py
│   │       ├── base_data_structure.py          # 基础数据结构模型
│   │       └── information_data_structure.py   # 资讯类数据结构模型
│   ├── producers/                # Kafka生产者实现
│   │   ├── __init__.py
│   │   ├── base_producer.py                   # Kafka生产者的抽象基类
│   │   └── information_mongo_to_kafka_producer.py # 具体的MongoDB到Kafka同步实现
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py
│   │   ├── decorators.py         # 装饰器模块，处理横切关注点
│   │   └── logger.py            # 日志模块
├── extend/                       # 扩展资源目录
│   └── elastic/                  # ElasticSearch相关文件
│       └── mapping/              # ES映射配置文件
├── runtime/                      # 运行时数据目录
│   ├── cursors/                  # 游标文件存储目录
│   └── log/                      # 日志文件目录
├── docker-compose/               # Docker Compose配置
│   └── docker-compose.yml
└── test/                         # 测试目录
    └── test.py
```

## 核心组件

### 数据源管理器

- MongoDB 管理器：单例模式设计，使用连接池管理 MongoDB 连接
- MySQL 管理器：使用连接池管理 MySQL 连接
- ElasticSearch 管理器：用于与 ElasticSearch 交互
- 易于扩展支持其他数据源管理器（如 PostgreSQL 等）

### Kafka 生产者基类 (BaseKafkaProducer)

- 抽象基类，定义了 Kafka 生产者的基本框架
- 提供统一的消息发送接口
- 支持消息转换和序列化功能

### 装饰器模块 (decorators.py)

- 提供日志记录和性能监控等横切关注点的处理

## 使用方法

### 数据同步

```bash
# 增量同步数据到Kafka
python run_producers.py --topic <topic_name> --data_type <data_type>

# 全量同步数据到Kafka
python run_producers.py --topic <topic_name> --data_type <data_type> --full_amount True

# 示例
python run_producers.py --topic temp4 --data_type information
```

支持的data_type:
- information: 资讯类数据

### 数据迁移

```bash
# 执行数据迁移任务
python run_migrate.py --task <task_name>

# 示例
python run_migrate.py --task info_to_nsfc
```

支持的task:
- info_to_nsfc: 资源信息到国自然基金数据迁移
- nsfc_to_es: 国自然基金资讯数据同步到ElasticSearch

## 配置说明

项目配置主要在 [application/config.py](file:///D:/company_project/kafka_prducer/kafka_prducer/application/config.py) 和 [application/settings.py](file:///D:/company_project/kafka_prducer/kafka_prducer/application/settings.py) 文件中定义，包括数据库连接信息、Kafka配置等。
