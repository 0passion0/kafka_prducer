from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from application.models.kafka_models.base_data_structure import DataStructure


# ---------- 主模型：InformationDataStructure ----------
class InformationDataStructure(DataStructure):
    """
    信息数据结构，用于在Kafka或应用内部传递结构化资讯数据。

    Attributes:
        data (DataPayload): 核心资讯内容
        metadata (MetaPayload): 资讯元数据，如来源、页面信息
        affiliated_data (AffiliatedPayload): 附件及关联数据，如链接和文件
    """
    data: DataPayload
    metadata: MetaPayload
    affiliated_data: AffiliatedPayload


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
    info_date: str
    info_section: List[str] = Field(default_factory=list)
    info_author: str
    info_source: str
    description: str


# ---------- 子模型：metadata ----------
class MetaPayload(BaseModel):
    """
    资讯元数据模型

    Attributes:
        marc_code (str): MARC（Machine-Readable Cataloging）代码
        main_site (str): 主站点或来源网站
        details_page (str): 详细页面 URL
    """
    marc_code: str
    main_site: str
    details_page: str


# ---------- 子模型：affiliated_data ----------
class AffiliatedPayload(BaseModel):
    """
    资讯附件数据模型

    Attributes:
        link_data (List[Dict[str, Any]]): 关联链接数据列表，每个字典包含链接相关信息
        files (List[Dict[str, Any]]): 关联文件数据列表，每个字典包含文件相关信息
    """
    link_data: List[Dict[str, Any]] = Field(default_factory=list)
    files: List[Dict[str, Any]] = Field(default_factory=list)
