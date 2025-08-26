from peewee import *

from application.db import BaseMysqlModel, get_database_connection


class NfscProjectType(BaseMysqlModel):
    project_type_id = IntegerField(index=True)
    project_type_name = CharField(null=True)
    project_type_description = CharField(null=True)

    class Meta:
        table_name = 'nfsc_project_type'
        database = get_database_connection('default1')  # 使用默认数据库
