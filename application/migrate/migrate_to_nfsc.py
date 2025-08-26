import json
from application.db import get_database_connection
from application.db.info.InformationSectionList import InformationSectionList
from application.db.info.InformationTagsRelationship import InformationTagsRelationship
from application.db.info.ResourceSource import ResourceSource
from application.db.info.InformationList import InformationList
from application.db.nfsc.NfscInfoList import NfscInfoList
from application.db.nfsc.NfscInfoType import NfscInfoType
from application.db.nfsc.NfscInformationSectionList import NfscInformationSectionList
from application.db.nfsc.NfscResourceSource import NfscResourceSource
from application.utils.logger import get_logger


class MigrateToNfsc:
    resource_source = ['www.nsfc.gov.cn']  # 需要迁移的资源源，暂时只有一个网站

    def __init__(self):
        """
        初始化迁移任务类，获取需要迁移的资源源ID和信息ID。
        """
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("初始化数据迁移任务")
        # 获取源ID集合，包含信息来源的ID
        self.source_ids = self.get_source_ids()
        # 获取需要迁移的所有信息ID
        self.information_ids = self.get_information_ids()
        self.logger.info(
            f"初始化完成，待迁移信息数量: {len(self.information_ids)}")

    def get_source_ids(self):
        """
        获取所有来源的源ID，排除已经存在的NFSC源ID。

        返回：
            set: 返回一个集合，包含所有待迁移的源ID
        """
        self.logger.info("开始获取资源源ID")
        # 获取所有资源源的source_id
        source_ids = set(record.source_id for record in ResourceSource.select(ResourceSource.source_id).where(
            ResourceSource.source_main_link.in_(self.resource_source)))

        self.logger.info(f"获取资源源ID完成，总共找到 {len(source_ids)} 个资源ID")
        return source_ids

    def get_information_ids(self):
        """
        获取需要迁移的所有信息ID，排除已经存在于NFSC中的信息。

        返回：
            set: 返回一个集合，包含需要迁移的所有信息ID
        """
        self.logger.info("开始获取信息ID")
        source_ids = self.source_ids
        # 获取所有信息列表的information_id
        information_ids = set(record.information_id for record in InformationList.select(
            InformationList.information_id).where(InformationList.source_id.in_(source_ids)))

        # 获取已经存在于NFSC中的信息ID
        info_ids = set(record.info_id for record in NfscInfoList.select(NfscInfoList.info_id).where(
            NfscInfoList.source_id.in_(source_ids)))

        # 返回需要迁移的信息ID，排除已经存在的
        result_ids = information_ids - info_ids
        self.logger.info(f"获取信息ID完成，总共找到 {len(result_ids)} 个待迁移的信息ID")
        return result_ids

    def fetch_information_data(self):
        """
        获取与信息相关的所有数据。

        返回：
            tuple: 包含信息列表、标签关系、信息章节列表和资源源数据的元组
        """
        self.logger.info("开始获取信息相关数据")
        # 获取信息列表
        information_list = InformationList.select().where(
            InformationList.information_id.in_(self.information_ids))
        # 获取信息标签关系
        information_tags_relationship = InformationTagsRelationship.select().where(
            InformationTagsRelationship.information_id.in_(self.information_ids))
        # 获取信息章节列表
        information_section_list = InformationSectionList.select().where(
            InformationSectionList.information_id.in_(self.information_ids)).dicts()

        # 获取NFSC已有的资源源ID
        nfsc_source_ids = set(
            record.source_id for record in NfscResourceSource.select(NfscResourceSource.source_id).where(
                NfscResourceSource.source_main_link.in_(self.resource_source)))
        # 获取资源源信息
        resource_source = ResourceSource.select().where(
            ResourceSource.source_id.in_(self.source_ids - nfsc_source_ids)).dicts()  # 排除已经存在的

        info_count = len(list(information_list))
        tags_count = len(list(information_tags_relationship))
        sections_count = len(list(information_section_list))
        sources_count = len(list(resource_source))

        self.logger.info(f"获取信息相关数据完成，信息列表: {info_count}条, 标签关系: {tags_count}条, "
                         f"章节列表: {sections_count}条, 资源源: {sources_count}条")

        return information_list, information_tags_relationship, information_section_list, resource_source

    def process_information_data(self, information_list, information_tags_relationship):
        """
        处理信息数据，转换成迁移所需的格式。

        参数：
            information_list (list): 信息列表
            information_tags_relationship (list): 信息标签关系列表

        返回：
            list: 处理后的信息数据列表，包含所有信息的相关字段
        """
        self.logger.info("开始处理信息数据")
        result_data_list = []  # 存储迁移结果的数据列表

        info_count = 0
        for record in information_list:
            info_if = record.information_id  # 信息ID
            info_name = record.information_name['zh']  # 信息名称（中文）
            original_link = record.original_link  # 原始链接
            publish_date = record.publish_date  # 发布日期
            project_type_id = '1'  # 项目类型ID，暂时固定为'1'
            info_academic_field = ''  # 学术领域，初始为空
            info_type_id = ''  # 信息类型ID，初始为空
            source_id = record.source_id  # 资源源ID

            # 遍历信息标签关系，获取相关字段
            for tag_record in information_tags_relationship:
                if tag_record.information_id == info_if:
                    tag_value = eval(tag_record.tag_value)  # 获取标签值
                    if tag_value:
                        # 如果标签值有多个元素，取第二个元素作为学术领域
                        info_academic_field = tag_value[1] if len(tag_value) > 1 else ''
                        # 根据标签值的第一个元素获取信息类型ID
                        info_type_id = NfscInfoType.select(NfscInfoType.info_type_id).where(
                            NfscInfoType.info_type_name == tag_value[0]).scalar()

            info_count += 1
            # 将处理后的信息数据添加到结果列表
            result_data_list.append({
                'info_id': info_if,
                'info_name': info_name,
                'original_link': original_link,
                'publish_time': str(publish_date),
                'project_type_id': project_type_id,
                'info_academic_field': info_academic_field,
                'info_type_id': info_type_id,
                'source_id': source_id
            })

            if info_count % 1000 == 0:
                self.logger.info(f"已处理 {info_count} 条信息数据")

        self.logger.info(f"信息数据处理完成，总共处理了 {info_count} 条信息")
        return result_data_list

    @get_database_connection('default1')
    def sync(self):
        """
        执行数据迁移的主操作，将信息、资源源、章节数据插入到NFSC数据库中。
        """
        self.logger.info("开始执行数据迁移")
        try:
            # 获取需要的所有数据
            information_list, information_tags_relationship, information_section_list, resource_source = self.fetch_information_data()
            # 处理信息数据
            result_data_list = self.process_information_data(information_list, information_tags_relationship)

            # 将处理后的数据插入到NFSC数据库中
            self.logger.info("开始插入NFSC信息列表数据")
            NfscInfoList.insert_many(result_data_list).execute()
            self.logger.info(f"插入NFSC信息列表数据完成，共插入 {len(result_data_list)} 条记录")

            self.logger.info("开始插入NFSC资源源数据")
            resource_source_list = list(resource_source)
            NfscResourceSource.insert_many(resource_source_list).execute()
            self.logger.info(f"插入NFSC资源源数据完成，共插入 {len(resource_source_list)} 条记录")

            self.logger.info("开始插入NFSC信息章节列表数据")
            information_section_list_data = list(information_section_list)
            NfscInformationSectionList.insert_many(information_section_list_data).execute()
            self.logger.info(f"插入NFSC信息章节列表数据完成，共插入 {len(information_section_list_data)} 条记录")

            self.logger.info("数据迁移完成")
        except Exception as e:
            self.logger.error(f"数据迁移过程中发生错误: {str(e)}", exc_info=True)
            raise


if __name__ == '__main__':
    # 创建迁移任务实例并执行迁移
    migrate_to_nfsc = MigrateToNfsc()
    migrate_to_nfsc.sync()
