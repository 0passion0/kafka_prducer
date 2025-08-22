from __future__ import annotations  # 允许前向引用
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class DataStructure(BaseModel):
    """

    :param uid: 唯一标识
    :param topic: 主题
    :param name: 名称
    :param created_at: 创建时间
    :param data_type: 数据类型标识
    :param tag_values: 标签值
    :param link_data: 附件列表
    """
    uid: str
    topic: str
    name: str
    created_at: str
    data_type: str
    tag_values: str
    link_data: List[Dict[str, Any]] = Field(default_factory=list)

    # class Config:
    #     """模型配置"""
    #     extra = "forbid"  # 禁止额外字段
    #     validate_assignment = True  # 支持赋值时校验
    #     frozen = True  # 模拟 __slots__ 效果，禁止动态添加属性

    def to_json(self, **kwargs) -> str:
        """
        将模型序列化为 JSON 字符串。

        修复：原实现返回 bytes，这里保证返回 str 并默认禁止 ASCII 转义以保留 Unicode 可读性。

        :return: JSON 字符串
        """
        # 使用 ensure_ascii=False 保持中文、特殊字符可读；允许通过 kwargs 覆盖其他序列化选项
        return self.model_dump_json(**kwargs).encode("utf-8")
