# -*- coding: utf-8 -*-
"""
国家自然科学基金信息导出器 — 重构版

该模块负责从数据库加载字典与分段数据，构建导出文档并写入 ElasticSearch。
"""

import json
import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from application.db.elastic_db import BaseElasticSearch, create_elastic_mapping
from application.config import ES_MAPPING_PATH
from application.db.mysql_db.nsfc import NsfcInfoList
from application.db.mysql_db.nsfc import NsfcInfoSectionList
from application.db.mysql_db.nsfc import NsfcInfoTypeDict
from application.db.mysql_db.nsfc.NsfcPublishProjectCodeDict import NsfcPublishProjectCodeDict
from application.db.mysql_db.nsfc import NsfcResourceSourceDict


class SectionTranslator:
    """分段数据处理与合并工具类"""

    @staticmethod
    def transformation(raw_sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        将数据库中分段原始记录转换为适合 ES 的结构，并拼接纯文本段落用于全文检索。

        :param raw_sections: 数据库取出的分段记录列表，每项为 dict
        :return: 包含 "section_list" 和 "section_text" 的字典
        """
        result_list: List[Dict[str, Any]] = []
        es_text_parts: List[str] = []

        for item in raw_sections:
            # 保留需要的字段并加入到结构化列表中
            result_list.append({
                "section_attr": item.get("section_attr"),
                "title_level": item.get("title_level"),
                "marc_code": item.get("marc_code"),
                "src_text": item.get("src_text"),
                "dst_text": item.get("dst_text"),
                "media_info": item.get("media_info"),
            })

            src_text = item.get("src_text")
            if not src_text:
                continue

            # src_text 预期为包含 children 的结构，逐个拼接 text 字段
            children = src_text.get("children", [])
            temp_parts: List[str] = []
            for child in children:
                try:
                    text_val = child.get("text") if isinstance(child, dict) else None
                    if text_val:
                        temp_parts.append(text_val)
                except Exception:
                    # 忽略单个子项解析错误，继续处理其它子项
                    continue

            if temp_parts:
                es_text_parts.append("".join(temp_parts))

        return {"section_list": result_list, "section_text": "\n".join(es_text_parts)}


class NsfcInfoExporter(BaseElasticSearch):
    """
    国家自然科学基金信息导出器（重构版）

    该类封装从数据库加载字典、合并分段、构建导出文档并写入 ElasticSearch 的流程。
    """

    index_name = "test_information_index"
    area_filter_default = {"0": "全国"}

    def __init__(self) -> None:
        """
        初始化导出器实例，准备缓存字典与日志。
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        # 数据缓存
        self._nsfc_info_sections: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self._nsfc_info_section_dict: Dict[int, Dict[str, Any]] = {}
        self._nsfc_info_type_dict: Dict[str, str] = {}
        self._nsfc_resource_source_dict: Dict[str, Dict[str, Any]] = {}
        self._nsfc_publish_project_code_dict: Dict[str, str] = {}
        self.nsfc_info_list: List[Dict[str, Any]] = []

    # ---------- 数据加载方法 ----------
    def load_sections(self) -> None:
        """
        从 NsfcInfoSectionList 加载分段并构建信息 ID 到分段结构的映射。
        """
        rows = NsfcInfoSectionList.select().order_by(
            NsfcInfoSectionList.information_id.asc(),
            NsfcInfoSectionList.section_order.asc()
        ).dicts()

        for row in rows:
            # 移除 create_time 等不必要字段（如果存在）
            row.pop("create_time", None)
            info_id = row.get("information_id")
            if info_id is None:
                continue
            self._nsfc_info_sections[info_id].append(row)

        # 处理每个信息的分段
        for info_id, sections in self._nsfc_info_sections.items():
            self._nsfc_info_section_dict[info_id] = SectionTranslator.transformation(sections)

    def load_type_dict(self) -> None:
        """
        加载信息类型字典（info_type_id -> info_type_name）。
        """
        for row in NsfcInfoTypeDict.select().dicts():
            tid = row.get("info_type_id")
            if tid is not None:
                self._nsfc_info_type_dict[str(tid)] = row.get("info_type_name", "")

    def load_source_dict(self) -> None:
        """
        加载资源来源字典（source_id -> 整行信息）。
        """
        for row in NsfcResourceSourceDict.select().dicts():
            sid = row.get("source_id")
            if sid is not None:
                self._nsfc_resource_source_dict[sid] = row

    def load_project_code_dict(self) -> None:
        """
        加载项目代码字典（apply_code -> code_name）。
        """
        for row in NsfcPublishProjectCodeDict.select().dicts():
            apply_code = row.get("apply_code")
            if apply_code is not None:
                self._nsfc_publish_project_code_dict[apply_code] = row.get("code_name", "")

    def load_all_dicts(self) -> None:
        """
        一次性加载所有需要的字典与分段数据。
        """
        self.load_sections()
        self.load_type_dict()
        self.load_source_dict()
        self.load_project_code_dict()

    # ---------- 构建导出对象的方法 ----------
    def _safe_source_name(self, source_id: Any) -> str:
        """
        从资源来源字典中安全获取中文名称，若缺失返回'未知'。
        """
        src = self._nsfc_resource_source_dict.get(source_id) or {}
        return (src.get("source_name") or {}).get("zh") or "未知"

    def _safe_source_main_link(self, source_id: Any) -> Optional[str]:
        src = self._nsfc_resource_source_dict.get(source_id) or {}
        return src.get("source_main_link")

    def _build_document(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        将数据库中单条 NsfcInfoList 记录转换为最终要写入 ES 的文档结构。

        :param row: 单条数据库记录（dict）
        :return: 结构化后的字典
        """
        info_id = row.get("information_id")

        # 处理类型与来源
        info_type_id = row.get("info_type_id")
        source_id = row.get("source_id")
        apply_code = row.get("apply_code")

        publish_time = row.get("publish_time") or row.get("create_time")
        publish_time_str = str(publish_time) if publish_time is not None else None

        section_info = self._nsfc_info_section_dict.get(info_id, {})
        return {
            "information_id": info_id,
            "info_type": {
                "info_type_id": info_type_id,
                "info_type_name": self._nsfc_info_type_dict.get(str(info_type_id), "")
            },
            "source_info": {
                "source_id": source_id,
                "source_name": self._safe_source_name(source_id),
                "source_main_link": self._safe_source_main_link(source_id),
            },
            "apply_info": {
                "apply_code": apply_code,
                "code_name": self._nsfc_publish_project_code_dict.get(apply_code, "其他"),
            },
            "area_info": {
                "area_id": row.get("province_id") or "0",
                "area_name": self.area_filter_default.get("0"),
            },
            "info_name": row.get("info_name"),
            "original_link": row.get("original_link"),
            "publish_time": publish_time_str,
            "sections_text": section_info.get("section_text"),
            "sections": section_info.get("section_list"),
        }

    def build_info_list(self) -> None:
        """
        从 NsfcInfoList 中读取数据并构建 self.nsfc_info_list。
        """
        self.nsfc_info_list = []
        for row in NsfcInfoList.select().dicts():
            try:
                doc = self._build_document(row)
                self.nsfc_info_list.append(doc)
            except Exception as exc:
                # 记录单条解析错误并继续处理其它记录
                self.logger.exception("构建信息文档失败，information_id=%s：%s", row.get("information_id"), exc)

    # ---------- ElasticSearch 相关方法 ----------
    def create_index_from_mapping(self, mapping_filename: str = "nsfc_info.json", cover: bool = True) -> bool:
        """
        根据 mapping 文件创建或覆盖 ES 索引。

        :param mapping_filename: mapping 文件名（位于 ES_MAPPING_PATH 下）
        :param cover: 是否覆盖已有索引
        :return: 创建成功返回 True，否则返回 False
        """
        mapping_path = f"{ES_MAPPING_PATH}/{mapping_filename}"
        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                mapping_info = json.load(f)
        except Exception as exc:
            self.logger.exception("读取 ES mapping 文件失败：%s", mapping_path)
            return False

        result = create_elastic_mapping(
            index_name=self.index_name,
            mapping_info=mapping_info,
            connect_sign="default",
            cover_sign=cover
        )

        if result.get("result"):
            self.logger.info("索引 %s 创建成功。", self.index_name)
            return True
        else:
            self.logger.error("索引创建失败：%s", result.get("msg"))
            return False

    def bulk_insert_to_es(self) -> bool:
        """
        使用 BaseElasticSearch.bulk_data 将已构建的文档批量写入 ES。

        :return: 成功返回 True，否则 False
        """
        if not self.nsfc_info_list:
            self.logger.warning("没有要写入的文档。")
            return True

        bulk_actions: List[Any] = []
        for doc in self.nsfc_info_list:
            # ES bulk 格式: action_line, data_line, ...
            bulk_actions.append({"index": {"_id": doc["information_id"]}})
            bulk_actions.append(doc)

        try:
            result = self.bulk_data(bulk_actions)
            if result.get("result"):
                processed = len(result.get("data", []))
                self.logger.info("批量插入成功，共处理 %d 条数据。", processed)
                return True
            else:
                self.logger.error("批量插入失败：%s", result.get("msg"))
                return False
        except Exception as exc:
            self.logger.exception("批量插入时发生异常：%s", exc)
            return False

    # ---------- 运行入口 ----------
    def run(self) -> bool:
        """
        执行完整流程：加载字典/分段 -> 构建文档 -> 创建索引 -> 批量写入 ES。

        :return: 全流程成功返回 True，否则 False
        """
        try:
            # 加载数据字典与分段
            self.load_all_dicts()
            # 构建文档列表
            self.build_info_list()
            # 创建索引
            if not self.create_index_from_mapping():
                self.logger.error("创建索引失败，终止导出。")
                return False
            # 批量写入 ES
            return self.bulk_insert_to_es()
        except Exception as exc:
            self.logger.exception("导出流程异常终止：%s", exc)
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    exporter = NsfcInfoExporter()
    success = exporter.run()
    if success:
        print("导出完成。")
    else:
        print("导出失败，请查看日志。")
