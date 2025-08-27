from peewee import (CharField, IntegerField,
                    DateTimeField, AutoField, SQL, TextField,
                    )
from playhouse.mysql_ext import JSONField

from application.db import get_database_connection
from application.db.BaseMysqlModel import BaseMysqlModel


class ResourceInformationSectionList(BaseMysqlModel):
    """资讯池段落列表"""
    section_id = CharField(index=True)  # 段落ID（si+时间戳+随机数）
    information_id = CharField(index=True)  # 资讯ID
    section_order = IntegerField()  # 段落排序
    section_attr = CharField(
        constraints=[SQL("DEFAULT '0'")])  # 段落属性（technique_object_article_section_attr_dict.attr_code）
    title_level = IntegerField(constraints=[SQL("DEFAULT 0")])  # 标题/项目级别：0-一级，1-二级...
    marc_code = CharField(null=True)  # 段落语言类型（marc_language_code_dict）
    src_text = JSONField(null=True)  # 段落原文（富文本 JSON）
    dst_text = JSONField(null=True)  # 段落译文（富文本 JSON）
    media_info = TextField(null=True)  # 媒体信息：图片/视频/音频/表格/公式等
    md5_encode = CharField(index=True)  # 段落 MD5 散列，用于去重


    class Meta:
        table_name = 'resource_information_section_list'
        database = get_database_connection('default')  # 使用默认数据库


