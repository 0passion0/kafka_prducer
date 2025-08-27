import json
from application.db import get_database_connection
from application.db.nsfc.NsfcInfoList import NsfcInfoList
from application.db.nsfc.NsfcInfoSectionList import NsfcInfoSectionList
from application.db.nsfc.NsfcInfoTypeDict import NsfcInfoTypeDict
from application.db.nsfc.NsfcResourceSourceDict import NsfcResourceSourceDict
from application.db.nsfc.NsfcPublishProjectCodeDict import NsfcPublishProjectCodeDict
from application.migrate.base_migrate import BaseMigrate


class MigrateToNsfc(BaseMigrate):
    resource_source = ['www.nsfc.gov.cn']  # 需要迁移的资源源，暂时只有一个网站

    def process_information_data(self, information_list, information_tags_relationship):
        """
        处理信息数据，转换成迁移所需的格式。

        参数：
            information_list (list): 信息列表
            information_tags_relationship (list): 信息标签关系列表

        返回：
            list: 处理后的信息数据列表，包含所有信息的相关字段
        """
        nsfc_info_departments_dict = self.get_information_departments_dict()

        result_data_list = []  # 存储迁移结果的数据列表

        for record in information_list:
            info_if = record.get('information_id')  # 信息ID
            info_name = record.get('information_name').get('zh')  # 信息名称（中文）
            original_link = record.get('original_link')  # 原始链接
            publish_date = record.get('publish_date')  # 发布日期
            info_academic_field = ''  # 学术领域，初始为空
            info_type_id = ''  # 信息类型ID，初始为空
            source_id = record.get('source_id')  # 资源源ID

            # 遍历信息标签关系，获取相关字段
            for tag_record in information_tags_relationship:
                if tag_record.get('information_id') == info_if:
                    tag_value = eval(tag_record.get('tag_value'))  # 获取标签值
                    if tag_value:
                        # 如果标签值有多个元素，取第二个元素作为学术领域
                        info_academic_field = tag_value[1] if len(tag_value) > 1 else ''
                        # 根据标签值的第一个元素获取信息类型ID
                        info_type_id = NsfcInfoTypeDict.select(NsfcInfoTypeDict.info_type_id).where(
                            NsfcInfoTypeDict.info_type_name == tag_value[0]).scalar()
            # 将处理后的信息数据添加到结果列表
            result_data_list.append({
                'information_id': info_if,
                'info_type_id': info_type_id,
                'apply_code': nsfc_info_departments_dict.get(info_academic_field,"*") if info_academic_field else None,
                'source_id': source_id,
                'info_name': info_name,
                'original_link': original_link,
                'publish_time': str(publish_date),
            })

        return result_data_list

    @get_database_connection('default1')
    def sync(self):
        result_dict = self.fetch_information_data()
        # 获取需要的所有数据
        information_list = result_dict['information_list']
        information_tags_relationship = result_dict['information_tags_relationship']
        information_section_list = result_dict['information_section_list']
        resource_source = result_dict['resource_source']
        # 处理信息数据
        result_data_list = self.process_information_data(information_list, information_tags_relationship)

        NsfcInfoList.insert_many(result_data_list).execute()
        resource_source_list = list(resource_source)
        NsfcResourceSourceDict.insert_many(resource_source_list).execute()
        information_section_list_data = list(information_section_list)
        NsfcInfoSectionList.insert_many(information_section_list_data).execute()

    def get_exclude_ids(self):
        """
        获取需要排除的 `information_id` 列表。

        :return: 待排除的 information_id 列表
        :rtype: list
        """
        exclude_ids = NsfcInfoList.select(NsfcInfoList.information_id)
        return set(record.information_id for record in exclude_ids)

    def get_exclude_source_ids(self):
        """
        获取需要排除的 `source_id` 列表。

        :return: 待排除的 source_id 列表
        :rtype: list
        """
        exclude_source_ids = NsfcResourceSourceDict.select(NsfcResourceSourceDict.source_id)
        return set(record.source_id for record in exclude_source_ids)

    @staticmethod
    def get_information_departments_dict():
        Nsfc_info_departments_dict = {}
        Nsfc_info_dep = NsfcPublishProjectCodeDict.select(NsfcPublishProjectCodeDict.apply_code,
                                                          NsfcPublishProjectCodeDict.code_name)
        for record in Nsfc_info_dep:
            Nsfc_info_departments_dict[record.code_name] = record.apply_code
        return Nsfc_info_departments_dict


if __name__ == '__main__':
    # 创建迁移任务实例并执行迁移
    migrate_to_nsfc = MigrateToNsfc()
    migrate_to_nsfc.sync()
