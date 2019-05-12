# coding=utf-8
# __author__: 737082820@qq.com(smart)

import sys

import cookielib
import urllib2
import random

# 伪装为浏览器
DEFAULT_USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]

DEFAULT_HEADER = {
    "User-Agent": random.choice(DEFAULT_USER_AGENTS)
}


def request_get(url, header=None, proxy_ip=None, cookies_flag=False, timeout=60):
    """
    伪装浏览器打开网页,Get方式\r\n

    header = {"User-Agent": "Mozilla/5.0..."} \r\n
    proxy_ip = {"http":"127.0.0.1:8080"} 或者  {"https":"127.0.0.1:8080"}

    :param url: 链接(http/https)
    :param header: 请求头,建议自定义,默认只添加 User-Agent
    :param proxy_ip: 代理IP,对应链接添加http/https代理
    :param cookies_flag: 添加Cookie,建议直接在header中添加
    :param timeout: 超时,默认60秒
    :return: 返回请求响应
    """
    # 添加代理
    if proxy_ip is not None:
        proxy = urllib2.ProxyHandler(proxy_ip)
        proxy_opener = urllib2.build_opener(proxy)
        urllib2.install_opener(proxy_opener)

    # 添加Cookies
    if cookies_flag:
        cookies = cookielib.CookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(cookies)
        cookies_opener = urllib2.build_opener(cookie_support)
        urllib2.install_opener(cookies_opener)

    # Request
    request = urllib2.Request(url=url, headers=DEFAULT_HEADER)
    # 手动添加其他请求头
    if header is not None:
        for key in header.keys():
            request.add_header(key, header[key])

    text = urllib2.urlopen(request, timeout=timeout).read()
    return text


def request_post(url, params, header=None, proxy_ip=None, cookies_flag=False, timeout=60):
    """
    伪装浏览器打开网页,Post方式\r\n

    params = 请求的具体参数，不一定是json \r\n
    header = {"User-Agent": "Mozilla/5.0..."} \r\n
    proxy_ip = {"http":"127.0.0.1:8080"} 或者  {"https":"127.0.0.1:8080"}

    :param url: 链接(http/https)
    :param params: 请求参数,json,urlencode编码等
    :param header: 请求头,建议自定义,默认只添加 User-Agent
    :param proxy_ip: 代理IP,对应链接添加http/https代理
    :param cookies_flag: 添加Cookie,建议直接在header中添加
    :param timeout: 超时,默认60秒
    :return: 返回请求响应
    """
    # 添加代理
    if proxy_ip is not None:
        proxy = urllib2.ProxyHandler(proxy_ip)
        proxy_opener = urllib2.build_opener(proxy)
        urllib2.install_opener(proxy_opener)

    # 添加Cookies
    if cookies_flag:
        cookies = cookielib.CookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(cookies)
        cookies_opener = urllib2.build_opener(cookie_support)
        urllib2.install_opener(cookies_opener)

    # Request
    request = urllib2.Request(url=url, data=params, headers=DEFAULT_HEADER)
    # 手动添加其他请求头
    if header is not None:
        for key in header.keys():
            request.add_header(key, header[key])

    text = urllib2.urlopen(request, timeout=timeout).read()
    return text


def req_get_image(url, header=None, timeout=60, min_size=0, max_size=sys.maxint):
    """
    GET 请求下载图片


    :param url: 链接(http/https)
    :param header: 请求头,建议自定义,默认只添加 User-Agent
    :param timeout: 超时,默认60秒
    :param max_size: 最大值,单位: byte
    :param min_size: 最小值,单位: byte
    :return: 返回请求响应
    """
    # Request
    request = urllib2.Request(url=url, headers=DEFAULT_HEADER)
    # 手动添加其他请求头
    if header is not None:
        for key in header.keys():
            request.add_header(key, header[key])

    response = urllib2.urlopen(request, timeout=timeout)
    # 对比图片大小
    img_size = int(response.headers['Content-Length'])
    if min_size <= img_size <= max_size:
        return response.read(), img_size
    return None, img_size
