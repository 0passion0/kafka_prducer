from peewee import *

from application.db import BaseMysqlModel, get_database_connection


class NsfcInfoTypeDict(BaseMysqlModel):
    info_type_id = IntegerField(index=True)
    info_type_name = CharField(null=True)
    info_type_description = CharField(null=True)

    class Meta:
        table_name = 'nsfc_info_type_dict'
        database = get_database_connection('default1')  # 使用默认数据库
