from peewee import (CharField, AutoField)

from playhouse.mysql_ext import JSONField
from application.db import get_database_connection
from application.db.BaseMysqlModel import BaseMysqlModel


class InformationTagsRelationship(BaseMysqlModel):
    """资讯与标签多对多关系表"""
    information_id = CharField(index=True)  # 主表ID（资讯ID）
    tag_code = CharField(index=True)  # 标签ID
    tag_value = CharField(null=True)  # 标签值

    class Meta:
        table_name = 'information_tags_relationship'
        database = get_database_connection('default')  # 使用默认数据库
