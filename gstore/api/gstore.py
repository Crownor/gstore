#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@ Author  : Yihan Guo
@ Mail    : crownor@icloud.com
@ File    : api.py
@ Date    : 2020/7/8
@ IDE     : PyCharm
@ Desc    : 用来处理gstore请求的
"""
import requests
import json
from typing import AnyStr, NoReturn, List, Dict, Optional
from guniflask.context import service
from guniflask.beans import SmartInitializingSingleton
from guniflask.config import settings
from urllib.parse import quote


@service
class GstoreAPI(SmartInitializingSingleton):
    """
    用来封装Gstore API请求的
    """

    def __init__(self):
        self.url = settings['GSTORE_URL']
        self.secret = settings['GSTORE_SECRET']
        self.key = settings['GSTORE_KEY']

    # TODO:为什么必须要加上这个呢？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？
    def after_singletons_instantiated(self):
        pass

    def __request__(self, params: Dict) -> Dict:
        """
        用于直接封装好API的请求
        @param params: 请求的参数,不需要添加key和secret
        @return: response的结果，直接load成Dict了
        """
        result = {}
        params['accesskeyid'] = self.key
        params['access_secret'] = self.secret
        # url = self.url + "?"
        # for key, value in params.items():
        #     url += (key + "=" + value + "&")
        try:
            response = requests.request("POST", self.url, params=params, verify=False)
            response = json.loads(response.content)
            result['response'] = response
        except Exception as e:
            print(e)
            result['error'] = str(e)
        return result

    def __get_all_db__(self) -> List:
        """
        用来获取所有的数据库，包含system
        @return: 一个数据库信息组成的list
        """
        params = {'action': "showDB"}
        response = self.__request__(params=params)
        if 'response' in response:
            return response['response']
        else:
            # TODO: 需要添加错误处理
            return None

    @property
    def dbList(self) -> List:
        """
        获得已有数据库的列表，主要格式如下
        [
            {
                "database":"jinrong",
                "creator":"root",
                "built_time":"2020-07-08 10:08:17",
                "status":"loaded"
            }
        ]
        @rtype: List
        @return: 已有数据库的列表
        """
        return self.__get_all_db__()

    def __get_db_details__(self, dbName: AnyStr) -> Dict:
        """
        获得指定数据库的详细信息
        @param dbName:数据库的名称
        @return: 数据库的详细信息
        """
        params = {
            'action': "monitorDB",
            'dbName': dbName
        }
        response = self.__request__(params=params)
        if 'response' in response:
            return response['response']
        else:
            # TODO: 需要添加错误处理
            return None

    def dbDetails(self, db: AnyStr) -> Dict:
        """
        获得指定数据库的详细信息，主要格式如下：
        {
            "msg": "ok",
            "connectionnum": 0,
            "StatusMsg": "success",
            "creator": "root",
            "triple num": 21440,
            "subject num": 14922,
            "entity num": 16652,
            "literalnum": 2,
            "StatusCode": 0,
            "built_time": "2020-07-08 10:08:17",
            "predicatenum": 3,
            "predicate num": 3,
            "database": "jinrong",
            "subjectnum": 14922,
            "success": 1,
            "cost_time": 1,
            "literal num": 2,
            "connection num": 0,
            "triplenum": 21440,
            "entitynum": 16652
        }
        @param db:指定数据库的名称
        @return:详细信息所构成的词典
        """
        return self.__get_db_details__(dbName=db)

    def __exec_sparql__(self, db: AnyStr, sparql: AnyStr) -> Dict:
        """
        用来执行sparql语句的
        @param db: 执行的数据库
        @param sparql: 执行的语句
        @return: 执行结果，原生的api response
        """
        params = {
            'action': "queryDB",
            'dbName': db,
            'sparql': sparql
        }
        response = self.__request__(params=params)
        if 'response' in response:
            return response['response']
        else:
            # TODO: 需要添加错误处理
            return None

    def exec(self, db: AnyStr, sparql: AnyStr) -> Dict:
        """

        @param db:
        @param sparql:
        @return:
        """
        # TODO: 这里需要添加对应的处理
        return self.__exec_sparql__(db=db, sparql=sparql)
