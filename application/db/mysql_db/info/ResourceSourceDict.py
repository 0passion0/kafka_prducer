from peewee import (CharField)

from playhouse.mysql_ext import JSONField
from application.db import get_database_connection
from application.db.mysql_db.base_mysql_model import BaseMysqlModel


class ResourceSourceDict(BaseMysqlModel):
    """来源表"""
    source_id = CharField(index=True)  # 来源ID，主键
    source_name = JSONField(null=True)  # 来源名，英文网站中文别名
    source_main_link = CharField()  # 来源主站链接
    source_description_image = JSONField(null=True)  # 来源描述图片
    source_intro = CharField(null=True)  # 来源简介

    class Meta:
        table_name = 'resource_source_dict'
        database = get_database_connection('default')  # 使用默认数据库
