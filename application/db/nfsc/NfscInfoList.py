from peewee import *

from application.db import get_database_connection, BaseMysqlModel


class NfscInfoList(BaseMysqlModel):
    info_id = CharField(index=True)
    info_type_id = CharField(index=True)
    project_type_id = CharField(index=True)
    source_id = CharField(index=True)
    province_id = CharField(null=True)
    info_name = CharField(null=True)
    info_academic_field = CharField(null=True)
    original_link=CharField(null=True)
    publish_time = DateField(null=True)


    class Meta:
        table_name = 'nfsc_info_list'
        database = get_database_connection('default1')  # 使用默认数据库