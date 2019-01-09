# coding=utf-8
# __author__: 737082820@qq.com(smart)
# 代理IP写入ES

from configparser import ConfigParser
from elasticsearch import Elasticsearch, NotFoundError
import json
import hashlib

from common.Log import Log
from common.SQLConnection import SQLConnection

CONN = SQLConnection()
SQL = "select ip,port,city,country from t_smart_proxy_ip"

# 初始配置信息
CONFIG = ConfigParser()
CONFIG.read("../sources/config.conf")

LOG = Log(file_name="smart_es_index_%Y-%m-%d.log", log_path=CONFIG.get("es", "log_path"))

INDEX = "proxy_ip"
DOC_TYPE = "ip"


def create_client():
    nodes = CONFIG.get("es", "ip").split(",")
    username = CONFIG.get("es", "username")
    passwd = CONFIG.get("es", "password")

    es_client = Elasticsearch(hosts=nodes, http_auth=(username, passwd))
    return es_client


def get_settings():
    settings = {}
    settings.setdefault("number_of_shards", "3")
    settings.setdefault("number_of_replicas", "1")
    return settings


def get_mapping():
    mapping = ""
    for row in open("../sources/proxy_ip_mapping.json", "r"):
        mapping += row
    mapping = json.dumps(json.loads(mapping), lambda o: o.__dict__)
    LOG.debug("Mapping: " + mapping)
    return mapping


def create_index(index, doc_type=None, settings=None, mappings=None):
    es = create_client()
    # 检测索引,类型是否存在
    if es.indices.exists(index=index):
        try:
            if es.indices.get_mapping(index=index, doc_type=doc_type):
                LOG.warning("[Mapping] index=" + index + " ,type=" + doc_type + " already existed")
                return True
        except NotFoundError:
            if mappings is not None:
                res = es.indices.put_mapping(index=index, doc_type=doc_type, body=mappings)
                LOG.debug("create mappings response: " + str(res))
                if "acknowledged" in res:
                    if res["acknowledged"]:
                        LOG.info("[Mapping] create " + index + "/" + doc_type + " success")
                    else:
                        LOG.info("[Mapping] create " + index + "/" + doc_type + " failed")
                    return res["acknowledged"]
                else:
                    raise Exception(res)
        except Exception, e:
            raise e
    else:
        if es.indices.create(index=index, body=settings):
            if doc_type is not None and mappings is not None:
                res = es.indices.put_mapping(index=index, doc_type=doc_type, body=mappings)
                LOG.debug("create mappings response: " + str(res))
                if "acknowledged" in res:
                    if res["acknowledged"]:
                        LOG.info("[Mapping] create " + index + "/" + doc_type + " success")
                    else:
                        LOG.info("[Mapping] create " + index + "/" + doc_type + " failed")
                    return res["acknowledged"]
                else:
                    raise Exception(res)
            else:
                LOG.info("[Index] create index=" + index + " success")
                return True
        else:
            LOG.error("create " + index + "/" + doc_type + " Failed")
            return False


def writer_data():
    es = create_client()
    result = CONN.select(SQL, 10)
    for row in result:
        ip = {}
        ip.setdefault("ip_addr", row[0])
        ip.setdefault("port", row[1])
        ip.setdefault("city", row[2])
        ip.setdefault("country", row[3])
        id = hashlib.md5(row[0] + "-" + str(row[1])).hexdigest()
        source = json.dumps(ip, lambda o: o.__dict__)
        LOG.debug(id + " : " + source)
        es.index(INDEX, doc_type=DOC_TYPE, body=source, id=id)


def bulk_writer_data():
    cache = []
    bulk_size = 5
    es = create_client()
    result = CONN.select(SQL, 13)
    for row in result:
        ip = {}
        ip.setdefault("ip_addr", row[0])
        ip.setdefault("port", row[1])
        ip.setdefault("city", row[2])
        ip.setdefault("country", row[3])
        id = hashlib.md5(row[0] + "-" + str(row[1])).hexdigest()
        ip.setdefault("id", id)
        source = json.dumps(ip, lambda o: o.__dict__)
        LOG.debug(id + " : " + source)
        # 1. 添加元信息
        new_action = {"_index": INDEX, "_type": DOC_TYPE, "_id": ip["id"]}
        # 2. 添加source
        action = {"index": new_action}
        cache.append(action)
        cache.append(source)

        if len(cache) >= bulk_size * 2:
            es.bulk(index=INDEX, doc_type=DOC_TYPE, body=cache)
            cache = []

    if len(cache) > 0:
        es.bulk(index=INDEX, doc_type=DOC_TYPE, body=cache)


if create_index("proxy_ip", doc_type="ip", settings=get_settings(), mappings=get_mapping()):
    bulk_writer_data()
