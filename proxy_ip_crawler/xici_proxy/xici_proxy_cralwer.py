# coding=utf-8
# __author__: 737082820@qq.com(smart)

import string

from bs4 import BeautifulSoup
from configparser import ConfigParser

from common.Log import Log
from common.HttpUtils import request_get

# 初始配置信息
CONFIG = ConfigParser()
CONFIG.read("../sources/config.conf")

LOG = Log(file_name="xici_proxy_crawler_%Y-%m-%d.log", log_path=CONFIG.get("xici", "log_path"))
URL = CONFIG.get("xici", "url")


def string_format(s):
    if not s:
        return s
    s = string.replace(s, "\n", "")
    s = string.strip(s)
    return s


def format_date(date):
    time = -1
    if u"天" in date:
        time = int(date[0:date.index(u"天")]) * 24 * 60 * 60
    elif u"小时" in date:
        time = int(date[0:date.index(u"小时")]) * 60 * 60
    elif u"分钟" in date:
        time = int(date[0:date.index(u"分钟")]) * 60
    return time


def xici_page_analysis(url):
    """
    解析页面
    :param url:
    :return:
    """
    bs = BeautifulSoup(request_get(url), "html5lib")

    page_num = bs.find("div", "pagination")
    current_num = int(page_num.find("em", "current").text)
    num_href = page_num.find_all("a")
    total_num = current_num
    for a in num_href:
        try:
            num = int(a.text)
            if total_num < num:
                total_num = num
        except Exception, e:
            pass
    LOG.info("current_num=%d ,total_num=%d" % (current_num, total_num))
    ips = []
    ip_list = bs.find("table").find_all("tr")
    for ip in ip_list:
        var = ip.find_all("td")
        if not var:
            continue
        d = ({})
        country = string_format(var[0].text)
        if not country:
            country = u"中国"
        d.setdefault("country", country)
        d.setdefault("ip_addr", string_format(var[1].text))
        d.setdefault("port", int(string_format(var[2].text)))
        d.setdefault("server_city", string_format(var[3].text))
        d.setdefault("anonymity", string_format(var[4].text))
        d.setdefault("type", string_format(var[5].text))
        speed = var[6].find("div")["title"]
        d.setdefault("speed", float(speed[0:len(speed) - 1]))
        conn_date = var[7].find("div")["title"]
        d.setdefault("connection_date", float(conn_date[0:len(conn_date) - 1]))
        d.setdefault("live_date", int(format_date(string_format(var[8].text))))
        d.setdefault("verify_date", "20" + string_format(var[9].text))
        ips.extend([d])
    return current_num, total_num, ips


if __name__ == "__main__":
    current_num, total_num, ips = xici_page_analysis(URL)
    for data in ips:
        sql = "insert into t_smart_proxy_ip (ip,port,city,country,anonymity,http_type,speed,connection_time," \
              "live_date,verify_date,state) values ('%s',%d,'%s','%s','%s','%s',%.3f,%.3f,%d,'%s',%d)" \
              % (data['ip_addr'], data['port'], data['server_city'], data['country'], data['anonymity']
                 , data['type'], data['speed'], data['connection_date'], data['live_date'], data['verify_date'], 0)
        LOG.info("[SQL] INSERT SQL = " + sql)
