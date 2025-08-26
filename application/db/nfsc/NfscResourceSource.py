from peewee import *

from playhouse.mysql_ext import JSONField

from application.db import BaseMysqlModel, get_database_connection


class NfscResourceSource(BaseMysqlModel):
    source_id = CharField(index=True)
    source_name = JSONField(null=True)  # json
    source_main_link = CharField()
    source_description_image = JSONField(null=True)  # json
    source_intro = CharField(null=True)

    class Meta:
        table_name = 'nfsc_resource_source'
        database = get_database_connection('default1')  # 使用默认数据库
