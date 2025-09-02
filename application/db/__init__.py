"""
数据库模块初始化文件
支持多个数据源配置，每个表可以使用不同的数据库
"""

from peewee import MySQLDatabase
from application.settings import MYSQL_DATABASES

# 存储数据库连接实例的字典
database_connections = {}


def init_database_connections():
    """
    初始化所有数据库连接
    """
    for db_key, db_config in MYSQL_DATABASES.items():
        database_connections[db_key] = MySQLDatabase(
            db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port']
        )


def get_database_connection(db_key='default'):
    """
    获取指定的数据库连接
    
    Args:
        db_key (str): 数据库配置键名
        
    Returns:
        MySQLDatabase: 数据库连接实例
    """
    if db_key not in database_connections:
        raise ValueError(f"Database connection '{db_key}' not found. Make sure to initialize connections first.")
    return database_connections[db_key]


# 初始化所有数据库连接
init_database_connections()

# 确保在导入模型前初始化数据库连接
from application.db.mysql_db.base_mysql_model import BaseMysqlModel
