from peewee import *
from playhouse.mysql_ext import JSONField

from application.db import BaseMysqlModel, get_database_connection


class NsfcInfoSectionList(BaseMysqlModel):
    section_id = CharField(index=True)
    information_id = CharField(index=True)
    section_order = IntegerField()
    section_attr = CharField(constraints=[SQL("DEFAULT '0'")])
    title_level = IntegerField(constraints=[SQL("DEFAULT 0")])
    marc_code = CharField(null=True)
    src_text = JSONField(null=True)  # json
    dst_text = JSONField(null=True)  # json
    media_info = TextField(null=True)
    md5_encode = CharField(index=True)

    class Meta:
        table_name = 'nsfc_info_section_list'
        database = get_database_connection('default1')  # 使用默认数据库