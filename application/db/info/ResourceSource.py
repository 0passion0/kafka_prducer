from peewee import (CharField, AutoField, IntegerField, SQL)

from playhouse.mysql_ext import JSONField
from application.db import get_database_connection
from application.db.BaseMysqlModel import BaseMysqlModel


class ResourceSource(BaseMysqlModel):
    """来源表"""
    source_id = CharField(index=True)  # 来源ID，主键
    source_name = JSONField(null=True)  # 来源名，英文网站中文别名
    source_main_link = CharField()  # 来源主站链接
    source_description_image = JSONField(null=True)  # 来源描述图片
    source_intro = CharField(null=True)  # 来源简介

    class Meta:
        table_name = 'resource_source'
        database = get_database_connection('default')  # 使用默认数据库


if __name__ == '__main__':
    # 查询 source_main_link 为 'www.nsfc.gov.cn' 的记录
    record = ResourceSource.get_or_none(ResourceSource.source_main_link == 'www.nsfc.gov.cn')

    if record:
        print(f"source_id: {record.source_id}")
    else:
        print("未找到对应记录")
