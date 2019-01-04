# coding=utf-8
# __author__: 737082820@qq.com(smart)

import os
import pymysql
import threading
from configparser import ConfigParser

# 默认mysql.conf配置文件路径
CUR_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(os.path.dirname(CUR_PATH), "./sources/mysql.conf")

CONFIG = ConfigParser()


# CONFIG.read(CUR_PATH + "../sources/mysql.conf")


class SQLConnection(object):
    _lock = threading.Lock()
    __conn = None
    __cursor = None

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = CONFIG_PATH
        self.config_path = config_path
        CONFIG.read(self.config_path)

        self.__conn = pymysql.connect(host=CONFIG.get('db', 'host'), port=CONFIG.getint('db', 'port'),
                                      user=CONFIG.get('db', 'user'), passwd=CONFIG.get('db', 'passwd'),
                                      db=CONFIG.get('db', 'db'),
                                      charset='utf8')
        self.__cursor = self.__conn.cursor()
        pass

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SQLConnection, '_instance'):
            with SQLConnection._lock:
                if not hasattr(SQLConnection, '_instance'):
                    SQLConnection._instance = SQLConnection(*args, **kwargs)
        return SQLConnection._instance

    def select(self, sql, size=0):
        """
        select * from t1
        :param sql: select SQL
        :param size: 返回行数,默认返回全部
        :return:
        """
        self.__cursor.execute(sql)
        if size <= 0:
            return self.__cursor.fetchall()
        else:
            return self.__cursor.fetchmany(size)

    def scroll(self, sql, position=0, size=100, mode="relative"):
        """
        对于导出大量数据时,建议采用scroll的方式

        :param sql: select SQL
        :param position: 开始位置
        :param size: 本次返回数据量
        :param mode: relative: 相对模式 ,absolute:绝对模式
        :return:
        """
        if size <= 0:
            raise Exception("size can't lower zero")
        self.__cursor.execute(sql)
        self.__cursor.scroll(position, mode)
        return self.__cursor.fetchmany(size)

    def execute(self, sql):
        """
        insert into t1 (name,age) values ("a","1")

        :param sql: Insert SQL
        :return: 返回影响的行数
        """
        success = self.__cursor.execute(sql)
        self.__conn.commit()
        return success

    def executemany(self, sql, args):
        """
        sql=insert into t1 (name,age) values (%s,%s)
        args= [["a","1"],["b","2"]]

        :param sql: Insert SQL
        :param args: 数组
        :return: 返回影响的行数
        """
        success = self.__cursor.executemany(sql, args)
        self.__conn.commit()
        return success

    def close(self):
        if self.__cursor:
            self.__cursor.close()
        if self.__conn:
            self.__conn.close()
        SQLConnection._instance = None
