from application.models.kafka_models.base_data_structure import DataStructure
from typing import ClassVar, Dict


class InformationDataStructure(DataStructure):
    """
        专用于资讯类数据的结构模型，继承自 DataStructure。

        本模型根据资讯业务场景定制了字段约束，明确了资讯发布信息、内容详情、
        语言类型、站点链接及附件信息等关键数据项的类型要求。

        主要特点：
        - 严格限制模型字段，不允许额外未声明字段，提升数据一致性。
        - 支持赋值时即时验证，保证字段变更符合预期格式。
        - 通过使用 __slots__ 优化内存使用和访问效率。
        - 约束明确：资讯发布日期、正文内容、作者、来源为必填且类型固定。
        - 元数据包含原始及过滤后的HTML代码、语言标识及相关链接。
        - 附件数据以字典形式存储，支持多样化资源管理。

        适用业务：
        - 资讯聚合平台、内容管理系统、信息发布服务等。
        - 需要对资讯结构数据进行严格格式控制和校验的场景。
    """
    # Pydantic v2 配置：
    # extra: forbid - 禁止额外字段，只允许模型中定义的字段
    # validate_assignment: True - 启用赋值时验证，确保字段值在赋值时也符合验证规则
    # arbitrary_types_allowed: True - 允许任意类型，不强制所有字段都是原生JSON类型
    # slots: True - 使用__slots__减少内存占用，提高访问速度
    model_config = {
        "extra": "forbid",
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
        "slots": True,
    }

    constraints: ClassVar[Dict[str, Dict[str, type]]] = {
        "data": {
            "info_date": str,  # 资讯发布时间，日期格式的字符串
            "info_section": list,  # 资讯正文的段落内容，纯文本格式
            "info_author": str,  # 资讯作者名称
            "info_source": str,  # 资讯来源，提供信息出处

        },
        "metadata": {
            "raw_html": str,  # 资讯的原始HTML代码，未经处理的页面内容
            "info_html": str,  # 过滤后的正文HTML，去除无关标签后的正文部分
            "marc_code": str,  # 资讯原语言类型，标识内容语言的代码
            "main_site": str,  # 主站链接，资讯所属主站的URL
            "details_page": str,  # 详情页链接，资讯具体内容页面的URL
            "resource_label": str,  # 资源标签，用于分类或标识资讯的关键词
        },
        "affiliated_data": {
            "link_data": list,  # 附件列表，包含附件的文件信息字典
            "files": list,  # 附件列表，包含附件的文件信息列表
        },
    }


if __name__ == '__main__':
    """
    示例 2：构造一个符合约束的 InformationDataStructure 实例（包含 constraints 中声明的必需键）。
    """

    info = InformationDataStructure(
        uid="info001",
        topic="新闻",
        name="示例信息",
        created_at="2025-08-13T11:00:00Z",
        data_type="information",
        data={
            "info_date": "2025-08-13",
            "info_section": "财经",
            "info_author": "张三",
            "info_source": "示例媒体"
        },
        metadata={
            "raw_html": "<html>...</html>",
            "info_html": "<div>...</div>",
            "marc_code": "0001",
            "main_site": "https://example.com",
            "details_page": "https://example.com/details/1",
            "resource_label": "新闻"
        },
        affiliated_data={
            "link_data": {"related": ["a", "b"]}
        }
    )

    print("创建成功:", info.uid)
    print("JSON:", info.to_json())
