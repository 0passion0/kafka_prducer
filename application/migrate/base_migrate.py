from application.db.mysql_db.info import ResourceInformationAttachmentList
from application.db.mysql_db.info.ResourceInformationList import ResourceInformationList
from application.db.mysql_db.info.ResourceInformationSectionList import ResourceInformationSectionList
from application.db.mysql_db.info.ResourceInformationTagsRelation import ResourceInformationTagsRelation
from application.db.mysql_db.info.ResourceSourceDict import ResourceSourceDict


class BaseMigrate:
    """
    数据迁移基类

    此类用于从数据库中抽取信息列表、信息标签关系、信息分区列表、
    信息附件列表以及资源来源等数据，提供统一的参数获取接口。

    子类可通过重写 ``resource_source`` 以及 ``get_exclude_ids``、
    ``get_exclude_source_ids`` 方法来定制具体的迁移逻辑。
    """

    # 需要处理的资源来源列表，由子类指定
    resource_source = []

    def fetch_information_data(self):
        """
        构建迁移所需的参数字典。

        :return: dict 包含以下键值：
            - information_list: 信息列表记录
            - information_tags_relationship: 信息与标签关系记录
            - information_section_list: 信息分区记录
            - information_attachments_list: 信息附件记录
            - resource_source: 资源来源记录
        :rtype: dict
        """
        # 获取需要排除的 `information_id`
        exclude_ids = self.get_exclude_ids()

        # 获取需要排除的 `source_id`
        exclude_source_ids = self.get_exclude_source_ids()

        # 从 ResourceSource 表中过滤出指定资源来源的 source_id
        source_ids = set(
            record.source_id
            for record in ResourceSourceDict.select(ResourceSourceDict.source_id).where(
                ResourceSourceDict.source_main_link.in_(self.resource_source)
            )
        )
        # 获取有效的 information_id（排除掉 exclude_ids，且来源于指定的 source_ids）
        information_ids = set(
            record.information_id
            for record in ResourceInformationList.select(ResourceInformationList.information_id).where(
                (~ResourceInformationList.information_id.in_(exclude_ids))
                & ResourceInformationList.source_id.in_(source_ids)
            )
        )
        # =======================================================================

        # 查询信息列表
        information_list = (
            ResourceInformationList.select()
            .where(ResourceInformationList.information_id.in_(information_ids))
            .dicts()
        )

        # 查询信息与标签的关系（目前与信息列表逻辑一致，可根据需求修改）
        information_tags_relationship = (
            ResourceInformationTagsRelation.select()
            .where(ResourceInformationTagsRelation.information_id.in_(information_ids))
            .dicts()
        )

        # 查询信息正文段落
        information_section_list = (
            ResourceInformationSectionList.select()
            .where(ResourceInformationSectionList.information_id.in_(information_ids))
            .dicts()
        )

        # 查询信息附件
        information_attachments_list = (
            ResourceInformationAttachmentList.select()
            .where(ResourceInformationAttachmentList.information_id.in_(information_ids))
            .dicts()
        )

        # 查询资源来源（排除掉 exclude_source_ids）
        resource_source = (
            ResourceSourceDict.select()
            .where(ResourceSourceDict.source_id.in_(source_ids - exclude_source_ids))
            .dicts()
        )

        return {
            "information_list": information_list,
            "information_tags_relationship": information_tags_relationship,
            "information_section_list": information_section_list,
            "information_attachments_list": information_attachments_list,
            "resource_source": resource_source,
        }

    def sync(self):
        """
        迁移执行入口方法。

        子类需要重写此方法，定义具体迁移逻辑。
        """
        pass

    def get_exclude_ids(self)-> set[str]:
        """
        获取需要排除的 `information_id` 列表。

        :return: 待排除的 information_id 列表
        :rtype: list
        """
        return {}

    def get_exclude_source_ids(self)-> set[str]:
        """
        获取需要排除的 `source_id` 列表。

        :return: 待排除的 source_id 列表
        :rtype: list
        """
        return {}
