# _*_ coding:utf-8 _*_
import time, urllib.request,requests
from bs4 import BeautifulSoup
import openpyxl
import xlwt
import peewee
import IpSpider
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
path = r'geckodriver.exe'


class JdSpider(object):
    """
        创建爬虫类
    """

    def __init__(self, Jd_mysql, data, proxy=True):
        if not data:
            self.param = self.defualt_param()
        else:
            self.param = data
        if proxy == True:
            self.proxy_set()
        else:
            self.proxy = ''
        self.load_page(Jd_mysql)

    def load_one(self, url):
        """
        加载网页
        :param data: 网页header和url
        :return: 爬取的网页源代码
        """
        if self.proxy != '':
            proxy = urllib.request.ProxyHandler(self.proxy)
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
            try:
                request = urllib.request.Request(url=url, headers=self.param['headers'])
                contect = urllib.request.urlopen(request,timeout=30)
            except requests.exceptions.ConnectionError:
                self.proxy_set(status=True)
                proxy = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(proxy)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(url=url, headers=self.param['headers'])
                contect = urllib.request.urlopen(request,timeout=30)

        else:
            request = urllib.request.Request(url=url, headers=self.param['headers'])
            contect = urllib.request.urlopen(request)
        return contect.read()

    def load_page(self, mysql_db):
        """
        网页page分析
        :param url: 爬去网页url
        :param num: 下载的页数
        :param src: 图片
        :return:
        """
        contect = self.load_one(self.param['url'])
        goodsArr = self.get_goods_info(contect)
        self.insert_goods_sql(mysql_db, goodsArr)
        self.param['page_count'] = self.param['page_count'] + 1
        if self.param['page_num'] > 1:
            for i in range(1, self.param['page_num']):
                self.habit(10)
                print("正在进入第", self.param['page_count'], '页')
                contect = self.load_one(self.param['url'] + str(i + 2))
                goodsArr = self.get_goods_info(contect)
                self.insert_goods_sql(mysql_db, goodsArr)
                self.param['page_count'] = self.param['page_count'] + 1

        self.stop()
        return True

    def get_goods_info(self, goodsInfoBoday):
        """
        获取商品信息
        :param goodsInfoBoday: 商品详情页面
        :return: 商品详细信息集合
        """
        soup = BeautifulSoup(goodsInfoBoday, "lxml")
        name_list = soup.select('div[class="gl-i-wrap"] > div > a > em')  # 商品名称
        goodsname_list = []
        for name in name_list:
            p_name = name.get_text().strip()
            goodsname_list.append(p_name)

        price_list = soup.select('div[class=gl-i-wrap] > div[class=p-price] > strong > i')  # 商品价格
        goodsprice_list = []
        for price in price_list:
            goodsprice_list.append(price.get_text().strip())

        sale_list = soup.select('div[class=gl-i-wrap] > div[class=p-commit] > strong > a')  # 商品销量
        goodssale_list = []
        for sale in sale_list:
            goodssale_list.append(sale.get_text().strip())

        url_list = soup.select('div[class=gl-i-wrap] > div[class=p-img] > a')  # 商品img
        goodsurl_list = []
        for url in url_list:
            url_link = 'https:' + url['href'].rsplit("//'", 1)[-1]  # 图片名
            goodsurl_list.append(url_link)

        goodsArr = {
            'goods_name': goodsname_list,
            # 'goods_img': goodsimg_list,
            'goods_price': goodsprice_list,
            'goods_sale': goodssale_list,
            'goods_sql_addtime': str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
            'goods_url': goodsurl_list,
        }

        return goodsArr

    def get_goods_params(self, url):
        """
        获取商品参数
        :param goodsArr: 商品基本信息
        :return: 单个商品完整信息
        """
        boday = self.load_one(url)
        soup = BeautifulSoup(boday, "lxml")

        goods_brand = soup.select('div[class=item] > a')
        brand_name = ''
        for brand in goods_brand:
            brand_name = brand_name + '/' + brand.get_text().strip()
        brand_name = brand_name.rsplit("/", 1)[0]

        goods_shop = soup.select('div[class=name] > a')
        shop_name = ''
        for shop in goods_shop:
            shop_name = shop_name + ' ' + shop['title']

        goods_pcate = soup.select('div[class="p-parameter"] > ul[class="p-parameter-list"] > li')
        pcate_name = ""
        for pcate in goods_pcate:
            pcate_name = pcate_name + ' ' + pcate['title']

        goods_param = {
            'goods_pcate': brand_name,
            'goods_brand': pcate_name,
            'goods_shop': shop_name
        }
        return goods_param

    def insert_goods_sql(self, Ant, goodsArr):
        """
        添加爬虫爬取的商品数据
        :param Ant: 实例化的peewee表对象
        :param goodsArr: 获取的商品集合
        :param self.param['goods_count']: 商品的个数
        :return: self.param['goods_count'] 商品的个数
        """
        for (name, price, sale, url) in zip(goodsArr['goods_name'], goodsArr['goods_price'],
                                                 goodsArr['goods_sale'], goodsArr['goods_url']):
            print('正在获取第 ',str(self.param['goods_count']),' 件商品的信息： 商品名称- ',name)
            # goods_param = self.get_goods_params(url)
            # print(goods_param['goods_pcate'])
            Ant.create(
                goods_name=name,
                # goods_img=img,
                goods_price=price,
                goods_sale=sale,
                goods_url=url,
                # goods_pcate="随便",
                # goods_brand=goods_param['goods_brand'],
                # goods_shop=goods_param['goods_shop'],
                goods_sql_addtime=goodsArr['goods_sql_addtime']
            )
            self.param['goods_count'] = self.param['goods_count'] + 1
            # print("获取成功")

    def stop(self):
        """
        关闭爬虫
        :return:
        """
        print("感谢您的使用：")
        print("- 爬虫停止工作，请重新启动爬虫 - JdSpider")
        pass

    def defualt_param(self):
        """
        默认值获取
        :return: 返回默认值
        """
        self.param = {
            "url": "http://search.jd.com/search?keyword=%E8%8C%B6&enc=utf-8&psort=3&ev=2762_32941%40&page=",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0"
            },
            "page_num": 10,
            "goods_count": 1,
            "page_count": 1
        }

    def habit(self, interval_time=3):
        """
        爬虫习惯设置
        :return:
        """
        self.time_interval_spider = interval_time  # 爬虫爬取信息间隔时间，防止IP被网站限制(默认3秒)
        time.sleep(self.time_interval_spider)  # 让爬虫休息设置的时间

    def proxy_set(self, proxy={}, status=False):
        """
        设置代理IP
        :param proxy:手动代理IP
        :return: 代理IP
        """
        if status == True:
            IP = IpSpider.IPSpider()
            ip_addr = IP.ip
        elif not proxy:
            IP = IpSpider.IPSpider()
            ip_addr = IP.ip
        else:
            ip_addr = proxy
        self.proxy = ip_addr


class Excel:
    # 当前行数
    _current_row = 1
    # 初始化，创建文件及写入title
    def __init__(self, sheet_name='sheet1'):
        # 表头，放到数组中
        title_label = ['商品编号', '商品名称', '价格', '商家', '商品详情地址', '时间', '是否自营', '关键字']
        self.write_work = xlwt.Workbook(encoding='ascii')
        self.write_sheet = self.write_work.add_sheet(sheet_name)
        for item in range(len(title_label)):
            self.write_sheet.write(0, item, label=title_label[item])
    # 写入内容
    def write_content(self, content):
        for item in range(len(content)):
            self.write_sheet.write(self._current_row, item, label=content[item])
        # 插入完一条记录后，换行
        self._current_row += 1
    # 保存文件（这里的'./dj_data.xls'是默认路径，如果调用此函数，没有传file_url参数，则使用'./dj_data.xls'）
    def save_file(self, file_url='./dj_data.xls'):
        try:
            self.write_work.save(file_url)
            print("文件保存成功！文件路径为：" + file_url)
        except IOError:
            print("文件保存失败！")

class JdMysql(object):
    def __init__(self):
        dbname = input("请输入数据库名：")
        user = input("请输入用户名：")
        passwd = input("请输入密码：")
        port = int(input("请输入端口号："))
        self.param = {
            'host' : "localhost",
            'dbname' : dbname,
            'user' : user,
            'passwd' : passwd,
            'port' : port,
        }
        self.conn = peewee.MySQLDatabase(
            host=self.param['host'],
            port=self.param['port'],
            user=self.param['user'],
            passwd=self.param['passwd'],
            database=self.param['dbname']
        )
    def Table(self,table='jdtable'):
        class jdtable(peewee.Model):
            goods_id = peewee.CharField(max_length=30)
            goods_name = peewee.CharField(max_length=200)
            goods_price = peewee.CharField(max_length=30)
            # goods_sale = peewee.CharField(max_length=30)
            goods_shop = peewee.CharField(max_length=150)
            goods_url = peewee.CharField(max_length=255)
            goods_sql_addtime = peewee.CharField(max_length=30)
            keyword = peewee.CharField(max_length=45)

            class Meta:
                database = self.conn
        return  jdtable

def get_html(url):
    # 模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.138 Safari/537.36',
        'accept-language': 'zh-CN,zh;q=0.9'
    }
    print("--> 正在获取网站信息")
    response = requests.get(url, headers=headers)  # 请求访问网站
    if response.status_code == 200:
        html = response.text  # 获取网页源码
        return html  # 返回网页源码
    else:
        print("获取网站信息失败！")

def isLimit(addr, num):
    # https://cart.jd.com/gate.action?pid=53301332796&pcount=158&ptype=1
    time.sleep(1)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    chrome_options.page_load_strategy = 'none'
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('blink-setting=imagesEnabled=false')
    chrome_options.add_argument('log_level=3')
    chrome_options.add_argument('--disable-plugins')

    browser = webdriver.Firefox(executable_path=path, options=chrome_options)
    browser.get(addr)
    num1 = browser.find_element_by_xpath('//input[@id="buy-num"]')
    num1.clear()
    num1.send_keys(num)
    # browser.sleep(1)
    time.sleep(1)
    result = browser.find_element_by_xpath('//a[@id="InitCartUrl"]').get_attribute("href")
    # print(result[-4:])
    browser.quit()
    if result[-4:] == 'none':
        return 'fail'
    else:
        return 'succ'

def getInfo(keyword, num, ziying, limit):
    # search_url = 'https://search.jd.com/Search?keyword=' + keyword + '&enc=utf-8&page=1'
    # html = get_html(search_url)
    # # 初始化BeautifulSoup库,并设置解析器
    # soup = BeautifulSoup(html, 'lxml')
    # # 商品列表
    # goods_list = soup.find_all('li', class_='gl-item')
    # 打印goods_list到控制台
    count = 0
    goodsname_list = []
    goodsno_list = []
    goodsprice_list = []
    goodsshop_list = []
    goodsaddr_list = []
    time_list = []
    zi_list = []
    page=0
    if ziying == 1:
        keyword+= ' 自营'

    while count < num:
        page += 1
        # 设置搜索关键字与页数 构建网址
        search_url = 'https://search.jd.com/Search?keyword=' + keyword + '&enc=utf-8' + '&page='+str(page)
        print('正在搜索第'+str(page)+'页，已获取'+str(count))
        html = get_html(search_url)
        # 初始化BeautifulSoup库,并设置解析器
        soup = BeautifulSoup(html, 'lxml')
        # 商品列表
        goods_list = soup.find_all('li', class_='gl-item')
        for li in goods_list:  # 遍历父节点
            # 商品编号
            no = li['data-sku']
            # 商品名称
            name = li.find(class_='p-name p-name-type-2').find('em').get_text()
            # 价格
            price = li.find(class_='p-price').find('i').get_text()
            # 商家
            shop = li.find(class_='p-shop').find('a').get_text()
            # 商品详情地址
            detail_addr = li.find(class_='p-name p-name-type-2').find('a')['href']
            thistime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            # 判断限购数量
            detail_addr = 'http:'+detail_addr
            limit_flag = isLimit(detail_addr, limit)
            if limit_flag == 'fail':
                continue

            # 自营
            if li.find(class_='p-icons') == None or li.find(class_='p-icons').find('i') == None:
                zi = '非自营'
            else:
                zi = li.find(class_='p-icons').find('i').get_text()
            # print(zi)
            if (zi == "自营" and ziying == 1) or (zi != "自营" and ziying == 0):
                goodsname_list.append(name)
                goodsno_list.append(no)
                goodsaddr_list.append(detail_addr)
                goodsshop_list.append(shop)
                goodsprice_list.append(price)
                time_list.append(thistime)
                zi_list.append(zi)
                # print(goodsname_list)
                # 计算已经爬取得到的数目
                count += 1
                if count >= num:
                    break
    return goodsno_list, goodsname_list, goodsprice_list, goodsshop_list, goodsaddr_list, time_list, zi_list

def database(txtName):
    Jd_Mysql = JdMysql()
    Jd_Model = Jd_Mysql.Table()
    with open(txtName, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip('\n')
            keyword = line.split()[0]
            num = int(line.split()[1])
            ziying = int(line.split()[2])
            limit_purchase_num = int(line.split()[3])
            goodsno_list, goodsname_list, goodsprice_list, goodsshop_list, goodsaddr_list, time_list, zi_list = getInfo(keyword, num, ziying, limit_purchase_num)

            # goodsno_list, goodsname_list, goodsprice_list, goodsshop_list, goodsaddr_list, time_list = getInfo(keyword, num, ziying, limit_purchase_num)
            goodsArr = {
                'goods_no': goodsno_list,
                'goods_name': goodsname_list,
                # 'goods_img': goodsimg_list,
                'goods_price': goodsprice_list,
                'goods_sql_addtime': str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                'goods_url': goodsaddr_list,
                'goods_shop': goodsshop_list
            }
            for (no, name, price, shop, url) in zip(goodsArr['goods_no'], goodsArr['goods_name'], goodsArr['goods_price'],
                                                goodsArr['goods_shop'], goodsArr['goods_url']):
                Jd_Model.create(
                    goods_id = no,
                    goods_name=name,
                    goods_price=price,
                    # goods_sale=sale,
                    goods_url=url,
                    goods_shop=shop,
                    goods_sql_addtime=goodsArr['goods_sql_addtime'],
                    keyword = keyword
                )

def save_XLS(txtName):
    # excel = openpyxl.load_workbook(dj_data)
    excel = Excel()
    with open(txtName, 'r', encoding='utf-8') as file:
        for line in file:

            line = line.strip('\n')
            # 每一行构成为：关键字 数量 是否自营 限制购买数量
            keyword = line.split()[0]
            num = int(line.split()[1])
            ziying = int(line.split()[2])
            limit_purchase_num = int(line.split()[3])
            goodsno_list, goodsname_list, goodsprice_list, goodsshop_list, goodsaddr_list, time_list, zi_list = getInfo(keyword, num, ziying, limit_purchase_num)
            goodsArr = {
                'goods_no': goodsno_list,
                'goods_name': goodsname_list,
                # 'goods_img': goodsimg_list,
                'goods_price': goodsprice_list,
                'goods_sql_addtime': str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                'goods_url': goodsaddr_list,
                'goods_shop': goodsshop_list,
                'goods_icon': zi_list
            }
            for (no, name, price, shop, url, zi) in zip(goodsArr['goods_no'], goodsArr['goods_name'], goodsArr['goods_price'],
                                                goodsArr['goods_shop'], goodsArr['goods_url'], goodsArr['goods_icon']):
                goods = [no, name, price, shop, url, goodsArr['goods_sql_addtime'], zi, keyword]
                # print('111')
                excel.write_content(goods)
            excel.write_work.save("dj_data.xls")

if __name__ == '__main__':
    # save_XLS('wula.txt')


    # 目标输入
    print('程序输入为文本文档，请将输入目标txt文档置于程序同目录下，文档格式为每一行为[关键字 爬取数量]\n如：\n\t白酒 4\n\t牛奶 5')
    txtName = input('请输入文档名称：')
    selection = int(input('选择结果保存方式：\n\t1. 直接保存为xls表格\n\t2. 保存到数据库\n请输入：'))
    if selection != 2:
        print("结果将保存在本目录下的dj_data.xls")
        save_XLS(txtName)
    else:
        print("将使用数据库保存")
        database(txtName)
    print('end')
