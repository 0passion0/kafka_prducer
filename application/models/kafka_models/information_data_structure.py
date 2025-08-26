from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from application.models.kafka_models.base_data_structure import DataStructure


# ---------- 子模型：data ----------
class DataPayload(BaseModel):
    """
    核心资讯数据模型

    Attributes:
        info_date (str): 资讯发布日期，格式如 'YYYY-MM-DD'
        info_section (List[str]): 资讯正文段落
        info_author (str): 资讯作者
        info_source (str): 资讯来源
        description (str): 资讯描述
    """
    info_date: Optional[str] = None
    info_section: List[Any] = Field(default_factory=list)
    info_author: Optional[str] = None
    description: Optional[str] = None


# ---------- 子模型：metadata ----------
class MetaPayload(BaseModel):
    """
    资讯元数据模型

    Attributes:
        marc_code (str): 语言代码
        details_page (str): 详细页面 URL
    """
    marc_code: str
    details_page: str


class InformationDataStructure(DataStructure):
    """
    信息数据结构，用于在Kafka或应用内部传递结构化资讯数据。

    Attributes:
        data (DataPayload): 核心资讯内容
        metadata (MetaPayload): 资讯元数据，如来源、页面信息
    """
    data: DataPayload
    metadata: MetaPayload
