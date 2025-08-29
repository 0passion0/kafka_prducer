import json
from collections import defaultdict

from application.db.nsfc.NsfcInfoList import NsfcInfoList
from application.db.nsfc.NsfcInfoSectionList import NsfcInfoSectionList
from application.db.nsfc.NsfcInfoTypeDict import NsfcInfoTypeDict
from application.db.nsfc.NsfcPublishProjectCodeDict import NsfcPublishProjectCodeDict
from application.db.nsfc.NsfcResourceSourceDict import NsfcResourceSourceDict


class NsfcInfoExporter:
    """
    国家自然科学基金信息导出器

    该类用于封装从数据库提取信息、构建字典、整合数据并最终导出为 JSON 文件的逻辑。
    """

    def __init__(self):
        """
        初始化必要的字典与数据缓存
        """
        self.area_filter = {"0": "全国"}
        self.nsfc_info_section = defaultdict(list)
        self.nsfc_info_type_dict = {}
        self.nsfc_resource_source_dict = {}
        self.nsfc_publish_project_code_dict = {}
        self.nsfc_info_section_dict = {}
        self.nsdc_info_list = []

    def load_sections(self):
        """
        加载信息分段数据并构建 section 映射
        """
        for i in NsfcInfoSectionList.select().order_by(
                NsfcInfoSectionList.information_id.asc(),
                NsfcInfoSectionList.section_order.asc()
        ).dicts():
            i.pop('create_time')
            self.nsfc_info_section[i['information_id']].append(i)

        for key, value in self.nsfc_info_section.items():
            self.nsfc_info_section_dict[key] = self.translate(value)

    def load_type_dict(self):
        """
        加载信息类型字典
        """
        for i in NsfcInfoTypeDict.select().dicts():
            self.nsfc_info_type_dict[str(i['info_type_id'])] = i['info_type_name']

    def load_source_dict(self):
        """
        加载资源来源字典
        """
        for i in NsfcResourceSourceDict.select().dicts():
            self.nsfc_resource_source_dict[i['source_id']] = i

    def load_project_code_dict(self):
        """
        加载项目代码字典
        """
        for i in NsfcPublishProjectCodeDict.select().dicts():
            self.nsfc_publish_project_code_dict[i['apply_code']] = i['code_name']

    def build_info_list(self):
        """
        构建完整的 NSFC 信息数据列表
        """
        for i in NsfcInfoList.select().dicts():
            self.nsdc_info_list.append(
                {
                    'information_id': i['information_id'],
                    'info_type': {
                        "info_type_id": i['info_type_id'],
                        "info_type_name": self.nsfc_info_type_dict.get(i['info_type_id'])
                    },
                    'source_info': {
                        "source_id": i['source_id'],
                        "source_name": self.nsfc_resource_source_dict.get(i['source_id']).get('source_name').get('zh'),
                        "source_main_link": self.nsfc_resource_source_dict.get(i['source_id']).get('source_main_link')
                    },
                    "apply_info": {
                        "apply_code": i['apply_code'],
                        "code_name": self.nsfc_publish_project_code_dict.get(i['apply_code'], "其他")
                    },
                    "area_info": {
                        "area_id": i['province_id'] or "0",
                        "area_name": self.area_filter.get("0")
                    },
                    "info_name": i['info_name'],
                    "original_link": i['original_link'],
                    "publish_time": str(i['publish_time']) if i['publish_time'] else str(i['create_time']),
                    "sections_text": self.nsfc_info_section_dict.get(i['information_id'], {}).get("section_text"),
                    "sections": self.nsfc_info_section_dict.get(i['information_id'], {}).get("section_list"),
                }
            )

    @staticmethod
    def translate(data):
        result_data = []
        es_text = ''
        for item in data:
            result_data.append(
                {
                    'section_attr': item['section_attr'],
                    'title_level': item['title_level'],
                    'marc_code': item['marc_code'],
                    'src_text': item['src_text'],
                    'dst_text': item['dst_text'],
                    'media_info': item['media_info'],
                }
            )
            temp_es_text = ''
            src_text = item.get('src_text')
            if not src_text:
                continue
            children = src_text.get('children', [])
            for text in children:
                if text.get('text'):
                    temp_es_text += text.get('text')
            es_text += temp_es_text + '\n'
        return {"section_list": result_data, "section_text": es_text}

    def export_to_json(self, filepath: str = "nsfc_info.json"):
        """
        导出最终数据为 JSON 文件

        :param filepath: 输出文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.nsdc_info_list, f, ensure_ascii=False, indent=4)

    def run(self, filepath: str = "nsfc_info.json"):
        """
        执行完整流程：加载数据、构建列表、导出 JSON

        :param filepath: 输出文件路径
        """
        self.load_sections()
        self.load_type_dict()
        self.load_source_dict()
        self.load_project_code_dict()
        self.build_info_list()
        self.export_to_json(filepath)


if __name__ == '__main__':
    if __name__ == "__main__":
        exporter = NsfcInfoExporter()
        exporter.run("nsfc_info.json")
