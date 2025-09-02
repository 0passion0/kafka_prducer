from application.db import get_database_connection
from application.db.mysql_db.nsfc.NsfcInfoList import NsfcInfoList
from application.db.mysql_db.nsfc.NsfcInfoSectionList import NsfcInfoSectionList
from application.db.mysql_db.nsfc.NsfcInfoTypeDict import NsfcInfoTypeDict
from application.db.mysql_db.nsfc.NsfcResourceSourceDict import NsfcResourceSourceDict
from application.db.mysql_db.info.ResourceInformationAttachmentList import ResourceInformationAttachmentList
from application.db.mysql_db.info.ResourceInformationList import ResourceInformationList
from application.db.mysql_db.info.ResourceInformationSectionList import ResourceInformationSectionList
from application.db.mysql_db.info.ResourceInformationTagsRelation import ResourceInformationTagsRelation
from application.db.mysql_db.info.ResourceSourceDict import ResourceSourceDict
from application.utils.logger import get_logger


class InfoToNsfc:
    resource_source = ['www.nsfc.gov.cn']
    apply_code_dict = {
        "数理科学部": "A",
        "数学物理科学部": "A",
        "化学科学部": "B",
        "生命科学部": "C",
        "地球科学部": "D",
        "工程与材料科学部": "E",
        "信息科学部": "F",
        "管理科学部": "G",
        "医学科学部": "H",
    }

    def __init__(self):
        self.logger = get_logger("info_to_nsfc")

    def fetch_information_data(self):
        self.logger.info("开始获取迁移所需信息数据。")

        exclude_ids = self.get_exclude_ids()
        self.logger.info(f"已排除 {len(exclude_ids)} 条信息ID。")

        exclude_source_ids = self.get_exclude_source_ids()
        self.logger.info(f"已排除 {len(exclude_source_ids)} 个资源来源ID。")

        source_ids = set(
            record.source_id
            for record in ResourceSourceDict.select(ResourceSourceDict.source_id).where(
                ResourceSourceDict.source_main_link.in_(self.resource_source)
            )
        )
        self.logger.info(f"符合迁移条件的 source_id 数量: {len(source_ids)}")

        information_ids = set(
            record.information_id
            for record in ResourceInformationList.select(ResourceInformationList.information_id).where(
                (~ResourceInformationList.information_id.in_(exclude_ids))
                & ResourceInformationList.source_id.in_(source_ids)
            )
        )
        self.logger.info(f"待迁移的有效信息数量: {len(information_ids)}")

        information_list = (
            ResourceInformationList.select()
            .where(ResourceInformationList.information_id.in_(information_ids))
            .dicts()
        )
        information_tags_relationship = (
            ResourceInformationTagsRelation.select()
            .where(ResourceInformationTagsRelation.information_id.in_(information_ids))
            .dicts()
        )
        information_section_list = (
            ResourceInformationSectionList.select()
            .where(ResourceInformationSectionList.information_id.in_(information_ids))
            .dicts()
        )
        information_attachments_list = (
            ResourceInformationAttachmentList.select()
            .where(ResourceInformationAttachmentList.information_id.in_(information_ids))
            .dicts()
        )
        resource_source = (
            ResourceSourceDict.select()
            .where(ResourceSourceDict.source_id.in_(source_ids - exclude_source_ids))
            .dicts()
        )

        self.logger.info("信息数据获取完成。")
        return {
            "information_list": information_list,
            "information_tags_relationship": information_tags_relationship,
            "information_section_list": information_section_list,
            "information_attachments_list": information_attachments_list,
            "resource_source": resource_source,
        }

    def process_information_data(self, information_list, information_tags_relationship):
        self.logger.info("开始处理信息数据。")
        result_data_list = []

        for record in information_list:
            info_if = record.get('information_id')
            info_name = record.get('information_name').get('zh')
            original_link = record.get('original_link')
            publish_date = record.get('publish_date')
            info_academic_field = ''
            info_type_id = ''
            source_id = record.get('source_id')

            for tag_record in information_tags_relationship:
                if tag_record.get('information_id') == info_if:
                    tag_value = eval(tag_record.get('tag_value'))
                    if tag_value:
                        info_academic_field = tag_value[1] if len(tag_value) > 1 else ''
                        info_type_id = NsfcInfoTypeDict.select(NsfcInfoTypeDict.info_type_id).where(
                            NsfcInfoTypeDict.info_type_name == tag_value[0]).scalar()

            result_data_list.append({
                'information_id': info_if,
                'info_type_id': info_type_id,
                'apply_code': self.apply_code_dict.get(info_academic_field, "*"),
                'source_id': source_id,
                'info_name': info_name,
                'original_link': original_link,
                'publish_time': str(publish_date),
            })

            self.logger.debug(f"处理信息ID {info_if}, 名称: {info_name}, 学术领域: {info_academic_field}")

        self.logger.info(f"信息数据处理完成，共处理 {len(result_data_list)} 条记录。")
        return result_data_list

    @get_database_connection('default1')
    def sync(self):
        self.logger.info("开始执行信息迁移同步任务。")
        result_dict = self.fetch_information_data()

        information_list = result_dict['information_list']
        information_tags_relationship = result_dict['information_tags_relationship']
        information_section_list = result_dict['information_section_list']
        resource_source = result_dict['resource_source']

        result_data_list = self.process_information_data(information_list, information_tags_relationship)

        NsfcInfoList.insert_many(result_data_list).execute()
        self.logger.info(f"已插入 NsfcInfoList {len(result_data_list)} 条记录。")

        resource_source_list = list(resource_source)
        NsfcResourceSourceDict.insert_many(resource_source_list).execute()
        self.logger.info(f"已插入 NsfcResourceSourceDict {len(resource_source_list)} 条记录。")

        information_section_list_data = list(information_section_list)
        NsfcInfoSectionList.insert_many(information_section_list_data).execute()
        self.logger.info(f"已插入 NsfcInfoSectionList {len(information_section_list_data)} 条记录。")

        self.logger.info("信息迁移同步任务完成。")

    def get_exclude_ids(self) -> set[str]:
        """
        获取需要排除的 `information_id` 列表。

        :return: 待排除的 information_id 列表
        :rtype: set
        """
        exclude_ids = NsfcInfoList.select(NsfcInfoList.information_id)
        return set(record.information_id for record in exclude_ids)

    def get_exclude_source_ids(self) -> set[str]:
        """
        获取需要排除的 `source_id` 列表。

        :return: 待排除的 source_id 列表
        :rtype: set
        """
        exclude_source_ids = NsfcResourceSourceDict.select(NsfcResourceSourceDict.source_id)
        return set(record.source_id for record in exclude_source_ids)


if __name__ == '__main__':
    # 创建迁移任务实例并执行迁移
    # migrate_to_nsfc = MigrateToNsfc()
    # migrate_to_nsfc.sync()
    for i in NsfcInfoList.select().dicts():
        print(i)
        break
