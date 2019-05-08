# coding=utf-8
# __author__: 737082820@qq.com(smart)
# __date__ : 2019-05-08 19:24:43
"""description
采用多线程版下载图片
"""
import os
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import argparse
from common.HttpUtils import request_get
from common.Log import Log
from common.SQLConnection import SQLConnection
from common.TimeUtils import date_format

# ========================== 常量 ==========================
HEADER = {
    # ":authority": "alpha.wallhaven.cc",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
}

# 本地保存路径
DIR_PATH = "D:/tmp/data/wallhaven_image/"
# 完整图片路径
IMAGE_FULL_URL = "https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-{0}.{1}"

LOG = Log(file_name="wallhaven_image_pool_%Y-%m-%d.log")
SQL_CONN = SQLConnection()

# Declare command-line flags.
argparser = argparse.ArgumentParser()

argparser.add_argument("-n", "--workers", help="使用线程数,最大不超过10", default=2, type=int)
argparser.add_argument("-s", "--start", help="图片开始编号", default=1, type=int)
argparser.add_argument("-e", "--end", help="图片结束编号,若不传则下载100张", default=1, type=int)

# 全局变量,计数器
download_image_counter = 0
# 全局的锁
lock = threading.Lock()


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
        return None
    except Exception, e:
        return e


def download_thread(start, end):
    LOG.info(threading.current_thread().name + '  download task : ' + str(start) + '-' + str(end))
    # 声明全局变量
    global download_image_counter
    download_success = 0

    while start <= end:
        image_id = -1
        # 下载数加1
        start += 1
        if lock.acquire():
            download_image_counter += 1  # 全局变量加1
            image_id = download_image_counter

            # 0. 校验图片是否已经下载,否则跳过
            sql = "select count(image_id) as image_cnt from t_smart_crawler_wallhaven where image_id=" + str(image_id)
            try:
                if SQL_CONN.select(sql)[0][0] == 1:
                    LOG.info(str(image_id) + ' had downloaded, continue')
                    continue
            except Exception, e:
                LOG.warning(str(image_id) + 'don\'t find , skip it. Error: ' + e.message)
                continue
            finally:
                lock.release()

        download_url = str.format(IMAGE_FULL_URL, str(image_id), 'jpg')
        # 1. 开始下载图片
        try:
            e = download_image(download_url, os.path.basename(download_url))
            # 尝试使用png下载
            if e is not None:
                download_url = str.format(IMAGE_FULL_URL, str(image_id), 'png')
                e = download_image(download_url, os.path.basename(download_url))

            if e is None:
                LOG.info('download image success ,url=' + download_url)
                # 2. 下载完成后,写入数据库,此处需要加锁,防止重复写
                insert = "insert into t_smart_crawler_wallhaven (image_id,image_url,download_date) values('" + \
                         str(image_id) + "','" + download_url + "','" + date_format(long(time.time())) + "')"
                SQL_CONN.execute(insert)
                LOG.info("Insert download image info success, SQL=" + insert)
                download_success += 1
            else:
                LOG.warning(str(image_id) + ' download error , url=' + download_url + ' ,ErrorMsg=' + e.msg)
        except Exception, e:
            LOG.error("image=" + download_url + " download fail or insert into Mysql fail, Error:" + e.message)
    return download_success


def thread_allocation_task(workers, start, end):
    '''
    根据线程数,下载图片数分配数量
    :param workers:
    :param start:
    :param end:
    :return:
    '''
    # 暂时采用平均分配
    tasks = []
    if workers <= 1:
        task = [start, end]
        tasks.append(task)
    else:
        avg_num = (end - start) / workers
        for i in range(0, workers):
            # 前N-1个都可以均匀分配
            if i + 1 < workers:
                task = [start, (i + 1) * avg_num]
            else:
                task = [start, end]
            tasks.append(task)
            start = (i + 1) * avg_num + 1
    return tasks


def pool_download(workers=2, start=1, end=100):
    LOG.info('download start=' + str(start) + ' ,end=' + str(end) + ' ,total=' + str(end - start + 1))
    pool = ThreadPoolExecutor(max_workers=workers)
    futures = []
    no_finished = 0
    success = 0
    for task in thread_allocation_task(workers, start, end):
        future = pool.submit(download_thread, task[0], task[1])
        futures.append(future)
        no_finished += 1

    while no_finished >= 1:
        for future in futures:
            if future.done():
                no_finished -= 1
                success += future.result()
    time.sleep(5)
    LOG.info('download image pool finished, success : ' + str(success) + ' ,total : ' + str(end - start + 1))


if __name__ == "__main__":
    workers = argparser.parse_args().workers
    start = argparser.parse_args().start
    end = argparser.parse_args().end
    if workers <= 0:
        raise Exception('params of workers must be grater zero,workers=' + str(workers))
    elif start <= 0:
        raise Exception('params of start must be grater zero,start=' + str(start))
    elif end < 0:
        raise Exception('params of end must be grater zero,end=' + str(end))
    if end == 1:
        end = start + 10
    pool_download(workers, start, end)
