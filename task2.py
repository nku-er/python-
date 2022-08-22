import socket
import re
from tkinter.messagebox import NO
from types import coroutine
from typing import Counter
from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.request import Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import urllib.parse
import requests

# key = ''
basic = ''
pages = set()
count = 0
MaxDepth = 100

def separate(url):
    if '//' in url:
        url = url.split('//')[1]
    if '/' in url:
        url = url.split('/')[0]
    return url

def getUrl(url: str):
    '''
        获取 URL
        :param url 地址
        :return 返回 bs 对象
    '''
    data = {}
    # head 添加请求头部，如果服务端通过请求头判断是否为机器访问，可以通过添加请求头
    head = {}
    head['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'
    head['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    data['type'] = 'AUTO'
    # data['i'] = input_data
    data['doctype'] = 'json'
    data['xmlVersion'] = '1.8'
    data['keyfrom'] = 'fanyi.web'
    data['ue'] = 'UTF-8'
    data['action'] = 'FY_BY_CLICKBUTTON'
    data['typoResult'] = 'true'
    data = urllib.parse.urlencode(data).encode('utf-8')
    # req = urllib.request.urlopen(url,data,head)  加了header 直接用urlopen会报错
    req = Request(url,data=None, headers=head)
    try:
        html = urlopen(req, timeout=1)
    except HTTPError as e:
        return None
    except socket.error as e:
        return None

    try:
        bsObj = BeautifulSoup(html.read(), 'html.parser')
    except AttributeError as e:
        return None
    except ValueError:
        return None
    return bsObj
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    #                   'AppleWebKit/537.36 (KHTML, like Gecko) '
    #                   'Chrome/81.0.4044.138 Safari/537.36',
    #     'accept-language': 'zh-CN,zh;q=0.9'
    # }
    # print("--> 正在获取网站信息")
    # response = requests.get(url, headers=headers)  # 请求访问网站
    # if response.status_code == 200:
    #     html = response.text  # 获取网页源码
    #     return html  # 返回网页源码
    # else:
    #     print("获取网站信息失败！")
    #     return None

def zhuanyi(url):
    new = eval(repr(url).replace(f'\\n', ''))
    new = eval(repr(new).replace(f'\\t', ''))
    new = eval(repr(new).replace(f'\\c', ''))
    return new

# base_url = ''
# url = ''
def getMorePages(base_url, relative_url: str = ""):
    '''
    获取更多页面
        :param base_url 基本 URL 地址
        :param relative_url 相对路径 URL
        :return None 失败
    '''
    global pages_error_count  # 访问出错页面计数器
    global count  # 用于限制递归深度
    global pages  # 采集过的页面
    global key
    count += 1
    if count == MaxDepth:
        return None
    # 拼接url，第一次默认为只有base_url
    url = urljoin(base_url, relative_url)
    bsObj = getUrl(url) # 返回一个bs对象
    if bsObj == None:
        pages_error_count += 1  # 失败页面计数
        print('bsObj none')
        return None

    if key in bsObj.text:
        print(url)
    pages.add(url)  # 保存处理过的页面
    print(pages)
    # base_url = url
    for link in bsObj.findAll('a'):
        if 'href' in link.attrs:
            # 如果找到新的链接
            nn = zhuanyi(link.attrs['href'])
            newUrl = urljoin(url, nn)
            # newUrl = urllib.parse.quote(newUrl)
            if newUrl not in pages:
                new = separate(newUrl)
                if basic != new:
                    continue
                newObj = getUrl(newUrl)
                if newObj == None:
                    print('// 5 fail')
                    pages_error_count += 1  # 失败页面计数
                    continue  # 返回到循环开始处

                getMorePages(url, nn)

if __name__ == '__main__':
    key = '年定报服务'
    print('start..')
    pages = set()  # 处理过的页面
    agent_list = []  # 保存采集到的代理数据
    pages_error_count = 0  # 访问出错页面计数器

    base_url = 'https://stats.tj.gov.cn'
    print(f"目标：{base_url}")
    basic = separate(base_url)
    print(basic)
    getMorePages(base_url)

    # print(zhuanyi(base_url))
