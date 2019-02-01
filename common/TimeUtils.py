# coding=utf-8
# __author__: 737082820@qq.com(smart)
# __date__ : 2019-02-01 16:48:46
"""description

"""

import time


def mill_format(date_time, format="%Y-%m-%d %H:%M:%S"):
    """
    yyyy-MM-dd HH:mm:ss 转为毫秒
    :param date_time:  yyyy-MM-dd HH:mm:ss
    :param format: 时间格式
    :return:
    """
    return long(time.mktime(time.strptime(date_time, format)))


def date_format(mill_time, format="%Y-%m-%d %H:%M:%S"):
    """
    毫秒转为 yyyy-MM-dd HH:mm:ss
    :param date_time: 毫秒
    :param format: 时间格式
    :return:
    """
    return time.strftime(format, time.localtime(mill_time))
