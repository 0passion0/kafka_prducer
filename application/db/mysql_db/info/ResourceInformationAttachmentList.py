from peewee import (CharField, IntegerField
                    )
from playhouse.mysql_ext import JSONField

from application.db import get_database_connection
from application.db.mysql_db.base_mysql_model import BaseMysqlModel


class ResourceInformationAttachmentList(BaseMysqlModel):
    """资讯附件表"""
    attachment_id = CharField(index=True)  # 资讯附件ID，可为空
    information_id = CharField(index=True, null=True)  # 资讯ID，外键
    attachment_name = CharField()  # 附件名称
    attachment_address = JSONField()  # 附件存储地址（OSS地址）
    display_order = IntegerField()  # 展示顺序

    class Meta:
        table_name = 'resource_information_attachment_list'
        database = get_database_connection('default')  # 使用默认数据库