from peewee import (CharField, IntegerField, AutoField, SQL, DateField
                    )
from playhouse.mysql_ext import JSONField

from application.db import get_database_connection
from application.db.BaseMysqlModel import BaseMysqlModel


class ResourceInformationList(BaseMysqlModel):
    """资讯主表，存储资讯基本信息"""
    information_id = CharField(index=True)  # 资讯ID，主键
    source_id = CharField(index=True)  # 来源ID，外键
    information_name = JSONField()  # 资讯名称，存储原名称和翻译等
    information_description = JSONField(null=True)  # 资讯描述，存储原描述和翻译等
    original_language = CharField()  # 资讯原语言类型（marc_language_code_dict 标识）
    cover = JSONField(null=True)  # 资讯封面（OSS地址）
    original_link = CharField()  # 原链接
    publish_date = DateField(null=True)  # 发布时间
    metadata = JSONField(null=True)  # 元数据（metadata_description 字段标识为 key）
    review_user = IntegerField()  # 审核员用户ID，0 表示无人工审核
    collection_method = CharField()  # 数据采集方式：0-机器采集，1-人工录入
    manual_review_status = CharField()  # 人工审核状态：0-待审核，1-审核通过，2-审核未通过
    machine_review_status = CharField()  # 机器审核状态：0-待审核，1-审核通过，2-审核未通过

    class Meta:
        table_name = 'resource_information_list'
        database = get_database_connection('default')  # 使用默认数据库

