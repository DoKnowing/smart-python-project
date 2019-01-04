# coding=utf-8
# __author__: 737082820@qq.com(smart)

import logging
import os
import time

# 默认log_path是存放日志的路径
CUR_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = os.path.join(os.path.dirname(CUR_PATH), "logs")


class Log(object):
    def __init__(self, file_name="%Y_%m_%d.log", level=logging.DEBUG, log_path=None):
        if log_path is None:
            log_path = LOG_PATH

        self.log_path = log_path
        # 如果不存在这个logs文件夹，就自动创建一个
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # 文件的命名
        self.logname = os.path.join(self.log_path, "%s" % time.strftime(file_name))
        self.logger = logging.getLogger()
        self.logger.setLevel(level)
        self.level = level

        # 日志输出格式
        self.formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)-8s: %(message)s")

    def __console(self, level, message):
        # 创建一个FileHandler，用于写到本地
        fh = logging.FileHandler(self.logname, "a", encoding="utf-8")
        fh.setLevel(self.level)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 创建一个StreamHandler,用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(self.level)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

        if level == logging.INFO:
            self.logger.info(message)
        elif level == logging.DEBUG:
            self.logger.debug(message)
        elif level == logging.WARNING:
            self.logger.warning(message)
        elif level == logging.ERROR:
            self.logger.error(message)
        # 这两行代码是为了避免日志输出重复问题
        self.logger.removeHandler(ch)
        self.logger.removeHandler(fh)
        # 关闭打开的文件
        fh.close()

    def debug(self, message):
        self.__console(logging.DEBUG, message)

    def info(self, message):
        self.__console(logging.INFO, message)

    def warning(self, message):
        self.__console(logging.WARNING, message)

    def error(self, message):
        self.__console(logging.ERROR, message)
