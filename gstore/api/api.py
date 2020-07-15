#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ Author  : Yihan Guo
@ Mail    : crownor@icloud.com
@ File    : api.py
@ Date    : 2020/7/8
@ IDE     : PyCharm
@ Desc    : 用于处理http请求的
"""
import json
from typing import AnyStr, Dict, List, NoReturn, Optional
from flask import request
from guniflask.web import blueprint, get_route, post_route
from .gstore import GstoreAPI
import itertools
import threading


@blueprint(url_prefix='/api/gstore')
class Gstore:
    """
    用于处理gstore相关的http请求
    """

    def __init__(self, gstore_api: GstoreAPI):
        self.gstore_api = gstore_api

    @post_route('/directRoutes')
    def directRoutes_response(self):
        """
        用来处理查询两个公司之间的关联路径（2-hop）。
        例如输入公司“招商局轮船股份有限公司”和“招商银行股份有限公司”，得到这两家公司之间的所有路径
        @return:
        """
        data = request.get_json()
        entities = data['entities']
        results = self.__query_direct_routes__(entities=entities, hop=2)
        routes: List = []
        for each_dist in results:
            routes += __analysis__(each_dist)
        return json.dumps(routes)

    def __query_direct_routes__(self, entities: List[AnyStr], hop: int) -> Optional[List[Dict]]:
        """
        用于查询两两实体之间的关联路径,先直接写死两跳
        @param entities: 实体列表，在这里是公司的名称
        @param hop:关联的跳数
        @return: 用于展示的List，每一个词典都是两两之间的关系
        """
        final_result = []
        # 便利任意两个（有序）
        for each_combine in list(itertools.permutations(entities, 2)):
            # 构造相应的sql
            sql = "select  * where { <file:///F:/d2r-server-0.7/holder8.nt#holder_copy/" + \
                  each_combine[0] + ">" + \
                  "?p ?o . ?o ?q  " + \
                  "<file:///F:/d2r-server-0.7/holder8.nt#holder_copy/" + each_combine[1] + "> }"
            response = self.gstore_api.exec(db="jinrong", sparql=sql)
            print(response)
            if response:
                tmp_result = {
                    "head": each_combine[0],
                    "tail": each_combine[1],
                    "bindings": response['data']['results']['bindings'],
                    "index": response['data']['head']['vars']
                }
                final_result.append(tmp_result)
        return final_result

    @post_route('/penetratingQuery')
    def penetratingQuery_response(self):
        """
        用来实现多层股权的穿透式查询
        @return:
        """
        data = request.get_json()
        entity = data['entity']
        hop = data['hop']
        result = dict(
            pre_result=self.__get_pre_entity__(entity, hop),
            next_result=self.__get_next_entity__(entity, hop)
        )
        return json.dumps(result)


    def __get_pre_entity__(self, entity: AnyStr, hop: int) -> List[AnyStr]:
        """
        获得上n跳的所有实体
        @param entity: 本级实体
        @param hop: 跳数
        @return: 上一级的所有实体
        """
        candidate = ["?a", "?b", "?c", "?d", "?e", "?f", "?g", "?h", "?i", "?j", "?k", "?l", "?m", "?n"]
        raw_node = []
        for each_hop in range(hop):
            s = candidate[2 * each_hop]
            p = candidate[2 * each_hop + 1]
            o = candidate[2 * each_hop + 2]
            raw_node += [s, p, o, "."]
        # 构造相应的sparql句子
        # 首先要去掉最后两个，因为分别是entity和相应的"."
        raw_node = raw_node[:-2]
        raw_sql = " ".join(raw_node)
        sql = "select  * where { " + raw_sql + " <file:///F:/d2r-server-0.7/holder8.nt#holder_copy/" + entity + ">  }"
        # sql = "select  * where { ?p ?o <file:///F:/d2r-server-0.7/holder8.nt#holder_copy/" + entity + ">  }"
        response = self.gstore_api.exec(db="jinrong", sparql=sql)
        if response:
            routes = {
                "head": None,
                "tail": entity,
                "bindings": response['data']['results']['bindings'],
                "index": response['data']['head']['vars']
            }
            result = __analysis__(routes)
        return result

    def __get_next_entity__(self, entity: AnyStr, hop: int) -> List[AnyStr]:
        """
        获得下n跳的所有实体
        @param entity:本级实体
        @param hop:相应的跳数
        @return: 下一级的所有实体
        """
        candidate = ["?a", "?b", "?c", "?d", "?e", "?f", "?g", "?h", "?i", "?j", "?k", "?l", "?m", "?n"]
        raw_node = []
        for each_hop in range(hop):
            s = candidate[2 * each_hop]
            p = candidate[2 * each_hop + 1]
            o = candidate[2 * each_hop + 2]
            raw_node += [s, p, o, "."]
        # 构造相应的sparql句子
        # 去掉最开始的头
        del raw_node[0]
        del raw_node[-1]
        raw_sql = " ".join(raw_node)
        sql = "select  * where { "  " <file:///F:/d2r-server-0.7/holder8.nt#holder_copy/" + entity + "> " + raw_sql + "  }"
        # sql = "select  * where { ?p ?o <file:///F:/d2r-server-0.7/holder8.nt#holder_copy/" + entity + ">  }"
        response = self.gstore_api.exec(db="jinrong", sparql=sql)
        if response:
            routes = {
                "head": entity,
                "tail": None,
                "bindings": response['data']['results']['bindings'],
                "index": response['data']['head']['vars']
            }
            result = __analysis__(routes)
        return result

    @post_route('/ringRoutes')
    def ringRoutes_response(self):
        """
        用来查询两家公司是否存在环形持股现象
        @return:
        """
        data = request.get_json()
        entity_0 = data['entity_0']
        entity_1 = data['entity_1']
        hop = data['hop']
        result = self.__check_ring_routes__(entity_0, entity_1, hop)
        return json.dumps(result)

    def __check_ring_routes__(self, entity_0: AnyStr, entity_1: AnyStr, hop: int) -> Dict:
        """
        用来检验两家公司是否存在环形持股
        @param entity_0: 第一家公司
        @param entity_1: 第二家公司
        @param hop:指定的环大小（单侧最长）
        @return: True：存在，False：不存在
        """
        # 根据群里说的不超过五跳，直接获得五跳之内的，然后做查询就好了
        entity_0_next = self.__get_next_entity__(entity_0, hop)
        entity_1_next = self.__get_next_entity__(entity_1, hop)
        chain0_1 = __check_include__(entity_0, entity_1_next)
        chain1_0 = __check_include__(entity_1, entity_0_next)
        if chain0_1 == [] or chain1_0 == []:
            return {"msg": "Do not exists"}
        # 然后对链路进行处理
        # 从entity0开始的链路
        print(chain0_1)
        print('\n\n')
        print(chain1_0)
        chain0 = list(set([x[:x.index(entity_1) + len(entity_1)] for x in chain1_0]))
        chain1 = list(set([x[:x.index(entity_0) + len(entity_0)] for x in chain0_1]))
        return {
            "msg": "存在",
            "data": {
                "0->1": chain0,
                "1->0": chain1
            }
        }


def __check_include__(entity: AnyStr, owns: List[AnyStr]) -> List[AnyStr]:
    """
    查询指定的entity是否在给定的列表内
    @param entity: 给定要查询的entity
    @param owns: 给定的持股列表
    @return: 存在的链路
    """
    result = []
    for each_chain in owns:
        if entity in each_chain:
            result.append(each_chain)
    return result


def __analysis__(routes: Dict) -> List[AnyStr]:
    """
    根据给的一个结果，构造为简单的文字表达形式
    @param routes:
    @return: 简单的文字表达形式
    """
    head = routes['head']
    tail = routes['tail']
    if head is not None:  # 如果存在头的话，说明要按照偶数项去取才能拿到实体,但是由于从0开始，得拿奇数
        # 首先确定顺序
        index = routes["index"][1::2]
        # 对与每一条路径来说
        final_routes = []
        for each_route in routes['bindings']:
            tmp_route = head
            # 按照顺序依次加入特定路径下的每一个节点
            for each_index in index:
                tmp_route += ("->" + each_route[each_index]['value'].replace(
                    "file:///F:/d2r-server-0.7/holder8.nt#holder_copy/", ""))
            # 添加尾节点
            if tail:
                tmp_route += ("->" + tail)
            final_routes.append(tmp_route)
    else:  # 说明头实体是空的，在结果里边要拿偶数项才能拿到实体
        index = routes["index"][::2]
        final_routes = []
        for each_route in routes['bindings']:
            tmp_route = ""
            # 按照顺序依次加入特定路径下的每一个节点
            for each_index in index:
                tmp_route += (each_route[each_index]['value'].replace(
                    "file:///F:/d2r-server-0.7/holder8.nt#holder_copy/", "")
                              + "->")
            # 添加尾节点
            tmp_route += tail
            final_routes.append(tmp_route)
    return final_routes


if __name__ == "__main__":
    test = {
        "head": "招商局轮船股份有限公司",
        "tail": "招商银行股份有限公司",
        "index": ["p", "o", "q"],
        "bindings": [{"p": {"type": "uri", "value": "http://localhost:2020/vocab/resource/holder_copy_holder_name"},
                      "q": {"type": "uri", "value": "http://localhost:2020/vocab/resource/holder_copy_holder_name"},
                      "o": {"type": "uri", "value": "file:///F:/d2r-server-0.7/holder8.nt#holder_copy/深圳市招融投资控股有限公司"}},
                     {"p": {"type": "uri", "value": "http://localhost:2020/vocab/resource/holder_copy_holder_name"},
                      "q": {"type": "uri", "value": "http://localhost:2020/vocab/resource/holder_copy_holder_name"},
                      "o": {"type": "uri", "value": "file:///F:/d2r-server-0.7/holder8.nt#holder_copy/深圳市晏清投资发展有限公司"}}]
    }

    routes = __analysis__(test)
    print(routes)
