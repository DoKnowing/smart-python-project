# coding=utf-8
# __author__: 737082820@qq.com(smart)

from configparser import ConfigParser
from elasticsearch import Elasticsearch

# 初始配置信息
CONFIG = ConfigParser()
CONFIG.read("../sources/config.conf")

nodes = CONFIG.get("es", "ip").split(",")
username = CONFIG.get("es", "username")
passwd = CONFIG.get("es", "password")

es_client = Elasticsearch(hosts=nodes, http_auth=(username, passwd))

query = "{\"query\":{\"term\":{\"uid\":\"25775614032\"}}}"
index_name = "friend_list"
index_type = "hago"
result = es_client.search(index=index_name, doc_type=index_type, body=query)
print result["hits"]["hits"]
