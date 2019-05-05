# coding=utf-8
# __author__: 737082820@qq.com(smart)
# __date__ : 2019-02-01 14:26:50
"""description

"""
import sys

# python 本地执行需要,对其他没有影响
sys.path.append("D:/smart_workspace/smart-python-project")
import argparse
import os
import time

from bs4 import BeautifulSoup

from common.HttpUtils import request_get
from common.Log import Log
from common.SQLConnection import SQLConnection
from common.TimeUtils import date_format

HEADER = {
    # ":authority": "alpha.wallhaven.cc",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
}

DIR_PATH = "D:/tmp/data/wallhaven_image/"

# URL句柄
# 可选条件,后期新增
# categories : 第一个1:general, 第二个1: anime(日本动漫) ,第三个1: people
# purity : 第一个1: sfw(shell fragment wound), 第二个1: sketchy(科幻)
# sorting : relevance,toplist,random..
# order : desc,asc
# resolutions : 像素,如: 3840x2880, 可选
# topRange : 1d,3d,1w,1M,3M,6M,1y 可选
SEARCH_URL = "https://alpha.wallhaven.cc/search?q={0}&categories=111&purity=100&sorting=relevance&order=desc&page={1}"

TOP_LIST_URL = "https://alpha.wallhaven.cc/toplist?page={0}"
LATEST_URL = "https://alpha.wallhaven.cc/latest?page={0}"
RANDOM_URL = "https://alpha.wallhaven.cc/random?page={0}"

# 完整图片路径
IMAGE_DETAIL_URL = "https://alpha.wallhaven.cc/wallpaper/{0}"
IMAGE_FULL_URL = "https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-"

LOG = Log(file_name="wallhaven_image_%Y-%m-%d.log")
SQL_CONN = SQLConnection()

# Declare command-line flags.
argparser = argparse.ArgumentParser()
argparser.add_argument(
    "action_type",
    choices=["query", "top_list", "latest", "random"],
    help="query: 查询指定内容,必须添加 --query_value 参数, top_list: 获取top列表, latest: 获取最近访问内容")

argparser.add_argument("-v", "--value", help="查询内容")

argparser.add_argument("-p", "--page_size", help="下载N页图片,每页有多张图片", default=10, type=int)


def download_image(image_url, file_name):
    """
    直接下载图片
    :param image_url:
    :return:
    """
    try:
        res = request_get(image_url, header=HEADER)
        image = open(DIR_PATH + file_name, "wb")
        image.write(res)
        image.close()
        return True
    except Exception, e:
        raise e


def browser_page(browser_url):
    """
    从浏览页面获取图片的唯一id
    :return:
    """
    image_ids = []
    # url校验
    if browser_url is None or (not browser_url.startswith("http://") and not browser_url.startswith("https://")):
        LOG.error("illegal url which is : " + str(browser_url))
        return image_ids
    retry = 3
    bs = None
    while retry > 0:
        try:
            bs = BeautifulSoup(request_get(browser_url, header=HEADER), "html5lib")
            break
        except Exception, e:
            ## 此处不进行重试
            retry -= 1
            LOG.warning("get image ids failed, url=" + browser_url + " ,Error: " + e.message + ", Retry " + str(3 - retry))
    if bs is None:
        LOG.error("get image ids failed, url=" + browser_url + " ,Error: " + e.message)
        return image_ids

    figures = bs.find_all("figure")
    for fg in figures:
        if "data-wallpaper-id" in fg.attrs:
            image_ids.append(str(fg["data-wallpaper-id"]))
    return image_ids


def get_image_full_url(action_type, page, value=None):
    if page <= 0:
        raise Exception("the page number must be greater than 0, page_size=" + str(page))
    current_page = 1
    count = 0
    while current_page <= page:
        LOG.info("start download image ,page=" + str(current_page))
        # 1. 获取当前页面所有的图片id
        if "top_list" == action_type:
            url = str.format(TOP_LIST_URL, current_page)
            LOG.info("get the image id of topList in wallhaven ,Page=" + str(current_page) + " ,url=" + url)
        elif "latest" == action_type:
            url = str.format(LATEST_URL, current_page)
            LOG.info("get the image id of latest in wallhaven ,Page=" + str(current_page) + " ,url=" + url)
        elif "random" == action_type:
            url = str.format(RANDOM_URL, current_page)
            LOG.info("get the image id of random in wallhaven ,Page=" + str(current_page) + " ,url=" + url)
        elif "query" == action_type:
            if value is None or value.strip() == "":
                raise Exception("query value can't be empty or NULL, value=" + str(value))
            # 将空格转为 +
            v_r = str.replace(value, " ", "+")
            url = str.format(SEARCH_URL, v_r, current_page)
            LOG.info("get the image id of query in wallhaven ,Page=" + str(current_page) + " ,url=" + url)
        else:
            raise Exception("unknown action_type which is : " + str(action_type))
        image_ids = browser_page(url)
        LOG.info("image ids: " + ", ".join(image_ids))

        # 当当前页没有图片时,结束任务
        if image_ids is None or len(image_ids) <= 0:
            LOG.info("download image finished !!!")
            break

        # 2. 下载图片
        # 判断图片是否已经被下载
        sql = "select image_id from t_smart_crawler_wallhaven where image_id in ('" + "','".join(image_ids) + "')"
        LOG.info("select image which had been download, SQL= " + sql)
        download_image_ids = {}  # 已经下载的图片id
        for image_id in SQL_CONN.select(sql):
            download_image_ids.setdefault(str(image_id[0]), "")
        LOG.debug(str(download_image_ids.keys()) + " has been download")

        for id in image_ids:
            if id not in download_image_ids.keys():
                # 获取url
                detail_url = str.format(IMAGE_DETAIL_URL, id)
                # 根据具体的url获取原始路径
                image_full_url = ""
                try:
                    detail_bs = BeautifulSoup(request_get(detail_url, header=HEADER), "html5lib")
                    image_full_url = "https:" + detail_bs.find("section").find("img")["src"]
                except Exception, e:
                    continue
                if not image_full_url.startswith(IMAGE_FULL_URL):
                    continue

                LOG.info("download image, url=" + image_full_url)
                try:
                    if download_image(image_full_url, os.path.basename(image_full_url)):
                        insert = "insert into t_smart_crawler_wallhaven (image_id,image_url,download_date) values('" + id + "','" + image_full_url + "','" + date_format(
                            long(time.time())) + "')"
                        SQL_CONN.execute(insert)
                        LOG.info("Insert download image info success, SQL=" + insert)
                        count += 1
                except Exception, e:
                    LOG.error(
                        "image=" + image_full_url + " download fail or insert into Mysql fail, Error:" + e.message)
            else:
                LOG.info(str(id) + " has been download")
        current_page += 1
    LOG.info("download image count : " + str(count) + " ,action_type=" + action_type + ",value=" + str(value))


if __name__ == "__main__":
    action_type = argparser.parse_args().action_type
    value = argparser.parse_args().value
    page = argparser.parse_args().page_size
    get_image_full_url(action_type, page, value)
