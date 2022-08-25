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
import xlwt

# key = ''
basic = ''
pages = set()
count = 0
MaxDepth = 100
result = 'result.txt'
#使用workbook方法，创建一个新的工作簿
book = xlwt.Workbook(encoding='utf-8',style_compression=0)
#添加一个sheet，名字为mysheet，参数overwrite就是说可不可以重复写入值，就是当单元格已经非空，你还要写入
sheet = book.add_sheet('mysheet',cell_overwrite_ok=True)

def separate(url):
    '''
    用于从给的网址中提取的函数
    如：http://a.com/a ->a.com
    '''
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
    # 以下设置的data无用
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

def zhuanyi(url):
    '''
    用于将网页中的href部分中的网址中的特殊符号删去
    如 \na.com-->a.com
    '''
    new = eval(repr(url).replace(f'\\n', ''))
    new = eval(repr(new).replace(f'\\t', ''))
    new = eval(repr(new).replace(f'\\c', ''))
    return new

def getMorePages(base_url, relative_url: str = ""):
    '''
    获取更多页面
        :param base_url 基本 URL 地址
        :param relative_url 相对路径 URL
        :return None 失败
    '''
    # f = open(result, 'w')
    global pages_error_count  # 访问出错页面计数器
    global count  # 用于限制递归深度
    global pages  # 采集过的页面
    global key
    # global row
    # count += 1
    # 每获得10个保存一次结果
    if count%10 == 0:
        print('yes')
        book.save('test.xls')

    if count == MaxDepth:
        # 最大值可提前设置，达到最大值后强制停止
        book.save('test.xls')
        return None
    # 拼接url，第一次默认为只有base_url
    url = urljoin(base_url, relative_url)
    bsObj = getUrl(url) # 返回一个bs对象
    if bsObj == None:
        pages_error_count += 1  # 失败页面计数
        print('bsObj none')
        return None
    
    # 如果页面中出现关键字且页面未被记录过
    if key in bsObj.text and url not in pages:
        sheet.write(count+1, 0, str(url))
        # 获取网页title
        title = bsObj.find('title').text.strip()
        sheet.write(count+1, 1, title)
        count += 1
        print(url)

    pages.add(url)  # 保存处理过的页面
    for link in bsObj.findAll('a'):
        if 'href' in link.attrs:
            # 如果找到新的链接
            nn = zhuanyi(link.attrs['href'])
            newUrl = urljoin(url, nn)
            # newUrl = urllib.parse.quote(newUrl)
            if newUrl not in pages:
                new = separate(newUrl)
                if basic != new:
                    # 如果获得新的页面不是要求的域名
                    continue
                newObj = getUrl(newUrl)
                if newObj == None:
                    print('// 5 fail')
                    pages_error_count += 1  # 失败页面计数
                    continue  # 返回到循环开始处

                getMorePages(url, nn)

if __name__ == '__main__':
    # key = '年定报服务'
    print('start..')
    key = input("请输入关键字：")
    pages = set()  # 处理过的页面
    agent_list = []  # 保存采集到的代理数据
    pages_error_count = 0  # 访问出错页面计数器

    # base_url = 'https://stats.tj.gov.cn'
    base_url = input('请输入网址：')
    print(f"目标：{base_url}")
    basic = separate(base_url)
    print(basic)
    # 写入excel第一行
    sheet.write(0,0,'网址')
    sheet.write(0,1,'标题')
    sheet.write(0,2,'日期')
    getMorePages('https://' + basic)
    # print(zhuanyi(base_url))
