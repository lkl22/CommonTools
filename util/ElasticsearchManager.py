# -*- coding: utf-8 -*-
# python 3.x
# Filename: ElasticsearchManager.py
# 定义一个ElasticsearchManager工具类实现从elasticsearch获取数据
from elasticsearch import Elasticsearch

from util.LogUtil import *

TAG = 'ElasticsearchManager'


class ElasticsearchManager:
    es = Elasticsearch(["http://localhost:9200"])

    @staticmethod
    def getFiled(id: str, fieldName: str):
        """
        获取elasticsearch数据
        :param id: doc id
        :param fieldName: field名
        :return: 指定filed的数据
        """
        try:
            result = ElasticsearchManager.es.search(index='.ds-filebeat-8.11.3-*', query={"match": {"_id": id}})
            return result['hits']['hits'][0]['_source'][fieldName]
        except Exception as e:
            LogUtil.e(TAG, 'getFiled 错误信息：', e)
            return None


if __name__ == "__main__":
    res = ElasticsearchManager.getFiled('36d6bb5a34b1d7b30cae4f6021f1c7d16f60ba19d47d9c53cf6a05c3c2cc9ca9', 'umlData')
    print(res)
