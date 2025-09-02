# -*- coding: utf-8 -*-

"""
# @Time    : 2022/4/26 14:59
# @User  : Mabin
# @Descriotion  :Elastic检索父类
"""
from application.settings import ELASTIC_CONNECTION
from elasticsearch import Elasticsearch
import logging


def create_elastic_connection(connect_sign="default") -> tuple[bool, str, Elasticsearch or None]:
    """
    初始化ElasticSearch数据库链接
    :author Mabin
    :param connect_sign:
    :return:
    """
    if not connect_sign:
        return False, "初始化ElasticSearch数据库链接时，传入数据库标识为空！", None
    connect_sign = str(connect_sign).lower()

    # 从数据库连接配置中，获取相关配置
    for connect_item in ELASTIC_CONNECTION:
        tmp_dgraph_sign = str(connect_item.get("sign", "")).lower()  # ElasticSearch连接标识
        if tmp_dgraph_sign != connect_sign:
            continue

        # 获取相关配置
        elastic_host = connect_item.get("host", None)  # 服务器地址
        elastic_user = connect_item.get("user", None)  # 账号
        elastic_password = connect_item.get("password", None)  # 账号
        elastic_scheme = connect_item.get("scheme", None)  # 连接协议
        elastic_port = connect_item.get("port", None)  # 服务器端口
        elastic_timeout = connect_item.get("timeout", None)  # 超时时间（秒）
        max_retries = connect_item.get("max_retries", None)  # 错误重试次数
        retry_on_timeout = connect_item.get("retry_on_timeout", False)  # 超时是否重试
        if not all([elastic_host, elastic_scheme, elastic_port]):
            continue

        # 实例化数据库连接
        client = Elasticsearch(
            hosts=elastic_host, http_auth=(elastic_user, elastic_password), port=elastic_port,
            scheme=elastic_scheme, timeout=elastic_timeout, max_retries=max_retries,
            retry_on_timeout=retry_on_timeout
        )

        return True, "ok！", client

    return False, f"未查询到ElasticSearch的数据库链接标识：{connect_sign}！", None


def create_elastic_mapping(index_name, mapping_info, connect_sign="default", cover_sign=False, index_alias=None):
    """
    创建索引，并添加相关mapping
    :author Mabin
    :param str index_name:索引名称
    :param dict mapping_info:Mapping字典，例如：{"dynamic": False, 'properties': {'approval_num': {'type': 'keyword'}}}
    :param str connect_sign:数据库链接标识
    :param bool cover_sign:对于已经存在的索引，是否删除覆盖，True为覆盖
    :param str index_alias:索引别名
    :return:
    """
    if not all([index_name, mapping_info, connect_sign]):
        return {"result": False, "msg": "创建索引时，传入参数为空！"}

    # 创建数据库连接
    client_result, client_msg, client_data = create_elastic_connection(connect_sign=connect_sign)
    if not client_result:
        return {"result": False, "msg": client_msg}

    if not isinstance(client_data, Elasticsearch):
        return {"result": False, "msg": "ElasticSearch数据库连接初始化失败！"}

    # 检查索引是否存在
    exist_result = client_data.indices.exists(index=index_name)
    if exist_result:
        # 存在相关索引
        if cover_sign:
            # 需要将原有索引删除
            client_data.indices.delete(index=index_name)
        else:
            # 不需要删除原有索引，则直接返回
            return {"result": False, "msg": "已经存在相关索引！"}

    # 创建索引
    create_result = client_data.indices.create(
        index=index_name, ignore=400
    )
    if not create_result.get("acknowledged", False):
        return {"result": False, "msg": f"索引创建失败！{create_result}"}

    # 创建mapping
    mapping_result = client_data.indices.put_mapping(
        index=index_name, body=mapping_info
    )
    if not mapping_result.get("acknowledged", False):
        return {"result": False, "msg": f"mapping创建失败！{mapping_result}"}

    # 创建索引别名
    if index_alias:
        # 为索引创建别名
        alias_result = client_data.indices.put_alias(index=index_name, name=index_alias)
        if not alias_result.get("acknowledged", False):
            return {"result": False, "msg": f"索引创建别名失败！{alias_result}"}

    return {"result": True, "msg": "ok！"}


class BaseElasticSearch:
    index_name: str = None
    client: Elasticsearch = None
    # 聚合数量上限
    max_aggregation_size = 500

    def __init__(self, connect_sign="default"):
        """
        初始化相关参数
        :author Mabin
        :param str connect_sign:数据库链接标识
        """
        if not self.index_name:
            raise Exception("初始化ElasticSearch时，未指明索引名称！")

        # 初始化数据库连接
        client_result, client_msg, client_data = create_elastic_connection(connect_sign=connect_sign)
        if not client_result:
            raise Exception(client_msg)
        self.client = client_data

        # 初始化日志
        self.logger = logging.getLogger('log')

    def get_by_elastic(self, document_id, query_field=None):
        """
        通过文档ID获取相关数据
        :author Mabin
        :param str document_id:文档ID
        :param list query_field:查询字段列表
        :return:
        """
        if not document_id:
            return {"result": False, "msg": "通过文档ID查询数据时，传入参数为空"}

        # 执行查询
        result = self.client.get(index=self.index_name, id=document_id, ignore=[400, 404],
                                 _source=query_field)

        # 检查是否查询成功
        found_sign = result.get("found", False)
        if not found_sign:
            return {"result": False, "msg": "未查询到相关数据！"}

        # 取出相关数据
        data_info = result.get("_source", {})
        return {"result": True, "msg": "ok！", "data": data_info}

    def get_multiple_elastic(self, document_list, query_field=None):
        """
        根据文档ID列表批量查询文档
        :author Mabin
        :param list document_list:文档ID列表
        :param list query_field:查询字段列表
        :return:
        """
        if not document_list:
            return {"result": False, "msg": "通过文档ID查询数据时，传入参数为空"}

        # 执行查询
        result = self.client.mget(body={'ids': document_list}, index=self.index_name, ignore=[400, 404],
                                  _source=query_field)

        # 获取相关数据
        data_info = result.get("docs", [])
        if not data_info:
            return {"result": False, "msg": "未查询到相关数据！"}

        # 组织返回数据
        buf = {}
        for data_item in data_info:
            document_id = data_item.get("_id", None)
            document_info = data_item.get("_source", {})
            if not all([document_id, document_info]):
                continue

            buf[document_id] = document_info

        return {"result": True, "msg": "ok！", "data": buf}

    def search_by_elastic(self, query_cond=None, **extra_param):
        """
        执行ES检索
        :author Mabin
        :param dict|None query_cond:查询数组，可为None
        :param any extra_param:额外参数：
            highlight=>高亮检索，例如：{"fields": {"title": {}}}
            first_row=>起始行数，自0开始
            list_rows=>每页显示行数
            order=>排序字段，例如：{"title": "desc"}
            query_field=>查询字段，例如：["project_id"]
        :return:
        """
        # 获取额外参数
        highlight = extra_param.get("highlight", None)  # 高亮检索，例如：{"fields": {"title": {}}}
        first_row = extra_param.get("first_row", 0)  # 起始行数，自0开始
        list_rows = extra_param.get("list_rows", 20)  # 每页显示行数
        order = extra_param.get("order", None)  # 排序字段，例如：{"title": "desc"}
        query_field = extra_param.get("query_field", None)  # 查询字段，例如：["project_id"]

        # 记录查询日志
        self.logger.debug(f"[ ES INPUT ] {query_cond} \n"
                          f"[ HIGHLIGHT ] {highlight} \n"
                          f"[ FIRST ROW ] {first_row} \n"
                          f"[ LIST ROWS ] {list_rows} \n"
                          f"[ ORDER ] {order} \n")

        # 执行查询
        result = self.client.search(
            index=self.index_name, query=query_cond, highlight=highlight, from_=first_row, size=list_rows, sort=order,
            ignore=[400, 404], _source=query_field
        )

        # 检查是否存在错误
        error_info = result.get("error", {})
        if error_info:
            self.logger.error(f"[ ES INPUT ] {query_cond} \n[ ERROR ] {error_info}")
            return {"result": False, "msg": error_info.get("reason", "ES查询出现错误！"), "data": []}

        # 取出相关数据
        hit_result = result.get("hits", {})
        if not hit_result:
            return {"result": True, "msg": "未查询到相关数据！", "data": []}
        hit_result = hit_result.get("hits", [])

        # 组织返回数据
        buf = []
        for data_item in hit_result:
            # 获取相关数据
            tmp_data = data_item.get("_source", {})
            if not tmp_data:
                continue

            # 检查是否存在高亮部分
            tmp_highlight = data_item.get("highlight", {})
            if tmp_highlight:
                # 将高亮信息在额外字段进行存储
                tmp_data["*highlight"] = {}
                for highlight_key, highlight_item in tmp_highlight.items():
                    # 将高亮数据覆盖原文数据
                    tmp_data[highlight_key] = highlight_item[0]
                    tmp_data["*highlight"][highlight_key] = highlight_item

            # 检查是否存在inner_hits部分
            tmp_inner_hits = data_item.get("inner_hits", {})
            if tmp_inner_hits:
                for inner_key, inner_item in tmp_inner_hits.items():
                    inner_item = inner_item.get("hits", {}).get("hits", [])
                    if not inner_item:
                        continue

                    tmp_data[inner_key] = inner_item

            buf.append(tmp_data)

        return {"result": True, "msg": "ok！", "data": buf}

    def aggregate_by_elastic(self, aggregate_cond, query_cond=None):
        """
        执行ES聚合检索
        :author Mabin
        :param dict aggregate_cond:聚合字典，例如：{"aggs_name": {"terms": {"field": "approval_num"}}}
        :param dict|None query_cond:查询数组，可为None
        :return:data返回值形如：
            {
                'aggs_name': {
                    'doc_count_error_upper_bound': 0,
                    'sum_other_doc_count': 0,
                    'buckets': [
                        {'key': '111', 'doc_count': 1},
                        {'key': '222', 'doc_count': 1},
                        {'key': '333', 'doc_count': 1}
                    ]
                }
            }
        """
        if not aggregate_cond:
            return {"result": False, "msg": "执行聚合查询时，聚合条件传入为空！", "data": {}}

        # 记录查询日志
        self.logger.debug(f"[ ES AGGREGATIONS ] {aggregate_cond} \n"
                          f"[ ES QUERY ] {query_cond} \n")

        # 执行查询
        result = self.client.search(
            index=self.index_name, query=query_cond, aggregations=aggregate_cond, ignore=[400, 404], size=0
        )

        # 检查是否存在错误
        error_info = result.get("error", {})
        if error_info:
            self.logger.error(f"[ ES INPUT ] {query_cond} \n[ ES AGGREGATE ] {aggregate_cond} \n[ ERROR ] {error_info}")
            return {"result": False, "msg": error_info.get("reason", "ES查询出现错误！"), "data": {}}

        # 取出聚合相关数据
        result = result.get("aggregations", {})
        if not result:
            return {"result": True, "msg": "未查询到聚合相关数据！", "data": {}}

        return {"result": True, "msg": "ok！", "data": result}

    def count_by_elastic(self, query_cond=None):
        """
        查询数量信息
        :author Mabin
        :param dict|None query_cond:查询数组，可为None
        :return:
        """
        # 组织查询字典
        if query_cond:
            query_cond = {
                "query": query_cond
            }

        # 执行查询
        result = self.client.count(index=self.index_name, body=query_cond, ignore=[400, 404])

        # 检查是否存在错误
        error_info = result.get("error", {})
        if error_info:
            self.logger.error(f"[ ES INPUT ] {query_cond} \n[ COUNT_ERROR ] {error_info}")
            return {"result": False, "msg": error_info.get("reason", "ES查询出现错误！"), "data": 0}

        # 获取相关数据
        return {"result": True, "msg": "ok！", "data": result.get("count", 0)}

    def index_by_elastic(self, index_data, document_id):
        """
        索引ES数据（更新或创建）
        :author Mabin
        :param dict index_data:索引数据，例如 {"title": "测试"}
        :param str document_id:ES文档ID
        :return:
        """
        if not all([index_data, document_id]):
            return {"result": False, "msg": "索引ES数据时，传入参数为空！"}

        # 进行索引
        result = self.client.index(
            index=self.index_name, document=index_data, id=document_id
        )

        # 检查是否存在错误
        error_info = result.get("error", {})
        if error_info:
            self.logger.error(f"[ ES INPUT ] {index_data} \n[ INDEX_ERROR ] {error_info}")
            return {"result": False, "msg": error_info.get("reason", "ES索引数据出现错误！")}

        # 获取索引类型：created/updated
        result = result.get("result", None)
        return {"result": True, "msg": "ok！", "data": result}

    def bulk_data(self, bulk_buf):
        """
        批量索引ES数据（更新或创建）
        :author Mabin
        :param list bulk_buf:待提交的数据列表
        :return:
        """
        if not bulk_buf:
            return {"result": False, "msg": "批量提交数据时，传入参数为空！"}

        # 将提交长度按1w切分为多个
        chunk_size = 10000
        chunk_list = [bulk_buf[i:i + chunk_size] for i in range(0, len(bulk_buf), chunk_size)]

        # 提交相关数据
        data_result = []
        for chunk_item in chunk_list:
            # 进行索引
            result = self.client.bulk(index=self.index_name, body=chunk_item)

            # 检查是否存在错误
            error_info = result.get("error", {})
            if error_info:
                self.logger.error(f"[ ES INPUT ] {chunk_item} \n[ ERROR ] {error_info}")
                return {"result": False, "msg": error_info.get("reason", "批量提交数据时出现错误！")}

            data_result.extend(result.get("items", []))

        return {"result": True, "msg": "ok！", "data": data_result}

    def analyze_word(self, target_text, analyzer_type="ik_smart"):
        """
        使用ES分词
        :author Mabin
        :param str target_text:待分词的文本
        :param str analyzer_type:分词类型，"ik_max_word","ik_smart"
        :return:
        """
        if not target_text:
            return {"result": False, "msg": "进行分词处理时，传入参数为空！"}

        # 向ES发送分词请求
        analyzer_result = self.client.indices.analyze(body={
            "analyzer": analyzer_type,
            "text": target_text
        })

        # 返回相关数据，data格式如：
        # [{'token': '仿生自组装', 'start_offset': 0, 'end_offset': 5, 'type': 'CN_WORD', 'position': 0},]
        return {"result": True, "msg": "ok！", "data": analyzer_result.get("tokens", [])}
