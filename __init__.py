"""
Kafka Producer 项目初始化文件
提供统一的模块导入接口
"""

# 数据源管理模块
from .models import MongoDBManager

# Kafka生产者模块
from .producers import BaseKafkaProducer, MongoDBtoKafka

# 游标管理模块
from .cursor_model import CursorManager, FileCursorManager

__all__ = [
    'MongoDBManager',
    'BaseKafkaProducer', 
    'MongoDBtoKafka',
    'CursorManager',
    'FileCursorManager'
]

# 项目版本信息
__version__ = '1.0.0'