from peewee import (
    MySQLDatabase, Model, IntegerField, DateTimeField, AutoField, SQL,
)
from application.settings import MYSQL_DATABASES


class BaseMysqlModel(Model):
    list_id = AutoField()  # 自增主键
    is_del = IntegerField(constraints=[SQL("DEFAULT 0")])  # 是否删除：0-否，1-是
    update_time = DateTimeField(null=True)  # 更新时间
    create_time = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])  # 创建时间

    class Meta:
        database = None  # 将在子类中设置具体的数据库连接

    @classmethod
    def set_database(cls, db_config_key='default'):
        """
        设置模型使用的数据库
        
        Args:
            db_config_key (str): 数据库配置键名，默认为'default'
        """
        if db_config_key in MYSQL_DATABASES:
            data_base = MYSQL_DATABASES[db_config_key]
            cls._meta.database = MySQLDatabase(
                data_base['database'],  # 数据库名称
                user=data_base['user'],  # 用户名
                password=data_base['password'],  # 密码
                host=data_base['host'],  # 主机地址
                port=data_base['port']  # 端口
            )
        else:
            raise ValueError(f"Database configuration '{db_config_key}' not found in MYSQL_DATABASES")

# class ResourceMetadataDescriptionList(BaseModel):
#     """字段描述表"""
#     list_id = AutoField()                            # 自增主键
#     field_id = CharField()                           # 字段ID，主键
#     field_owner = CharField()                        # 字段归属（资讯、视频、文献等）
#     field_code = CharField(index=True)               # 字段标识符，对应主表扩展字段的 key
#     field_name = CharField()                         # 字段名称
#     field_type = IntegerField()                      # 字段类型：1-固定字段，2-排除字段，3-拓展字段
#     field_description = CharField()                  # 字段描述
#     display_order = IntegerField()                   # 展示顺序
#     is_deleted = IntegerField(constraints=[SQL("DEFAULT 0")])  # 是否删除：0-否，1-是
#
#     class Meta:
#         table_name = 'resource_metadata_description_list'
#
#
# class ResourceSource(BaseModel):
#     """来源表"""
#     list_id = AutoField()                            # 自增主键
#     source_id = CharField(index=True)                # 来源ID，主键
#     source_name = JSONField(null=True)               # 来源名，英文网站中文别名
#     source_main_link = CharField()                   # 来源主站链接
#     source_description_image = JSONField(null=True)  # 来源描述图片
#     source_intro = CharField(null=True)              # 来源简介
#     is_deleted = IntegerField(constraints=[SQL("DEFAULT 0")])  # 是否删除：0-否，1-是
#     class Meta:
#         table_name = 'resource_source'
#
#
# class ResourceTagsList(BaseModel):
#     """标签表"""
#     list_id = AutoField()                            # 自增主键
#     tag_code = CharField(index=True)                 # 标签 code，主键
#     tag_type = CharField()                           # 标签类型
#     tag_owner = CharField()                          # 标签归属（资讯、视频、文献等）
#     tag_description = CharField(null=True)           # 标签描述
#     is_deleted = IntegerField(constraints=[SQL("DEFAULT 0")])  # 是否删除：0-否，1-是
#
#
#     class Meta:
#         table_name = 'resource_tags_list'
#
#
# if __name__ == '__main__':
#     from datetime import datetime
#
#     info = InformationList.create(
#         collection_method='test',
#         information_id='demo-001',
#         information_name={'zh-CN': '测试标题'},
#         information_description={'zh-CN': '测试描述'},
#         original_language='zh-CN',
#         cover={'url': 'https://test.com/cover.jpg'},
#         metadata={'tags': ['news', 'demo']},
#         original_link='https://test.com',
#         machine_review_status='pending',
#         manual_review_status='pending',
#         review_user=0,
#         source_id='src-001',
#         create_time=datetime.now(),
#         update_time=datetime.now()
#     )
#     print(info.list_id)  # 打印刚插入的自增主键
