from peewee import *

from application.db import BaseMysqlModel, get_database_connection


class NsfcPublishProjectCodeDict(BaseMysqlModel):
    apply_code = CharField(index=True)
    code_name = CharField()
    parent_code = CharField(null=True)

    class Meta:
        table_name = 'nsfc_project_code_dict'
        database = get_database_connection('default1')  # 使用默认数据库
