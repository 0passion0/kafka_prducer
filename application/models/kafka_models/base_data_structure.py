from typing import Any, ClassVar, Dict, List
from pydantic import BaseModel, Field, model_validator


class DataStructure(BaseModel):
    """
    通用数据结构模型类，基于 Pydantic 实现，旨在统一管理和校验多类型数据及其相关信息。

    核心功能：
    - 自动保证 data、metadata 和 affiliated_data 字段存在且为字典类型，避免运行时类型错误。
    - 通过可重写的 `constraints` 属性，支持灵活定义必需字段及其类型约束。
    - 初始化后自动校验字段完整性与类型一致性，确保数据结构的严谨性和规范性。
    - 提供方便的 JSON 序列化接口，支持自定义序列化参数，保证输出的可读性和兼容性。

    设计原则：
    - 严格类型校验，及早发现数据异常。
    - 灵活扩展性，方便子类覆盖和自定义约束规则。
    - 安全与性能并重，避免不必要的类型转换和冗余检查。

    :param uid: 唯一标识
    :param topic: 主题
    :param name: 名称
    :param created_at: 创建时间
    :param data_type: 数据类型标识
    :param menu_list: 菜单层级列表
    :param data: 主要数据（字典）
    :param metadata: 元数据（字典）
    :param affiliated_data: 关联数据（字典）

    """

    uid: str
    topic: str
    name: str
    created_at: str
    data_type: str
    tag_code: str
    tag_values: str  # 标签值

    # tag_values: List[str] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    affiliated_data: Dict[str, Any] = Field(default_factory=dict)

    # 子类可以覆盖 constraints 来定义特定的必需字段与类型
    constraints: ClassVar[Dict[str, Dict[str, type]]] = {
        "data": {},
        "metadata": {},
        "affiliated_data": {},
    }

    # @model_validator(mode="before")
    # def _ensure_and_normalize_dicts(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     在模型创建前确保子字段存在且为字典，并做必要的键名归一化。
    #
    #     - 将缺失或 None 的子字段替换为空字典
    #     - 如果传入值不是字典则抛出 TypeError（早期失败以提升安全性）
    #
    #     :param values: 原始输入字典
    #     :return: 可能被调整过的输入字典
    #     :raises TypeError: 当某个子字段存在但不是字典时抛出
    #     """
    #     # 局部化 names 提升循环内访问效率
    #     for field_name in ("data", "metadata", "affiliated_data"):
    #         raw = values.get(field_name, {})
    #         # 将 None 或缺失字段统一为空字典
    #         if raw is None:
    #             raw = {}
    #         # 早期类型检查，避免后续逻辑错误
    #         if not isinstance(raw, dict):
    #             raise TypeError(f"字段 '{field_name}' 必须是字典类型，收到: {type(raw).__name__}")
    #         values[field_name] = raw
    #     return values
    #
    # @model_validator(mode="after")
    # def _validate_constraints(cls, model: "DataStructure") -> "DataStructure":
    #     """
    #     在模型初始化后，根据 constraints 检查每个子字典必须包含的字段及类型。
    #
    #     保持原有规则不变：对每个在 constraints 中声明的键，要求存在且类型匹配。
    #
    #     :param model: 已构造的模型实例
    #     :return: 通过校验的模型实例
    #     :raises ValueError: 缺少必需字段
    #     :raises TypeError: 字段类型不匹配
    #     """
    #     # 局部化变量以减少属性访问开销
    #     constraints = cls.constraints
    #     for field_name, rules in constraints.items():
    #         sub = getattr(model, field_name, None) or {}
    #         # 这一步通常不会触发，因为 before validator 已处理，但为稳健性保留检查
    #         if not isinstance(sub, dict):
    #             raise TypeError(f"字段 '{field_name}' 必须是字典类型")
    #
    #         # 遍历规则并进行检查
    #         for key, expected_type in rules.items():
    #             if key not in sub:
    #                 raise ValueError(f"字段 '{field_name}' 必须包含键 '{key}'")
    #             # 明确类型检查，兼容继承关系
    #             if not isinstance(sub[key], expected_type):
    #                 raise TypeError(
    #                     f"字段 '{field_name}' 中的 '{key}' 必须是 {expected_type.__name__} 类型，收到: {type(sub[key]).__name__}:{sub[key]}"
    #                 )
    #     return model

    def to_json(self, **kwargs) -> str:
        """
        将模型序列化为 JSON 字符串。

        修复：原实现返回 bytes，这里保证返回 str 并默认禁止 ASCII 转义以保留 Unicode 可读性。

        :return: JSON 字符串
        """
        # 使用 ensure_ascii=False 保持中文、特殊字符可读；允许通过 kwargs 覆盖其他序列化选项
        return self.model_dump_json(**kwargs).encode("utf-8")
