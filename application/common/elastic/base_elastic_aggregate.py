# -*- coding: utf-8 -*-

"""
# @Time    : 2024/4/25 10:12
# @User  : Mabin
# @Descriotion  :ES聚合处理的接口
"""
from abc import ABC, abstractmethod


class BaseElasticAggregate(ABC):
    @abstractmethod
    def handle_aggregate_data(self, search_cond, query_filter=None, **extra_param):
        """
        处理ES的聚合查询
        :author Mabin
        :param list search_cond: 查询条件列表
        :param dict query_filter:过滤条件字典
        :param any extra_param:额外输入，用于拓展函数
            query_num=>查询数量
        :return:
        """
        pass

    @abstractmethod
    def create_aggregation(self, **extra_param):
        """
        创建ES聚合查询的聚合条件
        :author Mabin
        :param any extra_param:额外输入，用于拓展函数
            query_num=>查询数量
        :return:
        """
        pass

    @abstractmethod
    def parse_result(self, result):
        """
        处理aggregate_by_elastic函数的data数据，并得到最终聚合结果
        :author Mabin
        :param dict result:聚合结果
        :return:
        """
        pass
