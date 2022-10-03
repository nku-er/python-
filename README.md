# python-

任务1文件包括：Spider_main.py，spider_input.txt，IpSpider.py

Spider_main.py为程序  京东爬虫

spider_input.txt为程序Spider_main.py的输入文件，可更改

task2.py为第二个任务的文件，即在给定域名下搜索相关关键字。包括task2.py, weibo.py, config.json

### 使用task2进行微博关键字搜索时的注意
由于微博中的爬取需要模拟登录，因此请按照以下步骤设置config.json文件。

#### 1. 使用chrome浏览器登录微博。
此处推荐chrome，如果使用其他浏览器，可能无法按照以下步骤获取cookie信息。
#### 2. 在微博搜索框中输入关键字进行搜索，并在界面按下“`shift`+ `ctrl`+`i`”。

![图片](https://user-images.githubusercontent.com/68672834/187065052-69ef23e1-7b09-4477-ba52-5f02a8f2c52b.png)

#### 3. 找到如下内容
选择`network`->刷新页面->在右侧`name`下找到`weibo?q=`字样
![图片](https://user-images.githubusercontent.com/68672834/187065197-40c1492c-ec94-4a56-90cc-6d8cd4a2a68f.png)

#### 4. 找到cookie
单击`weibo?q=`，在`Request Headers`下找到cookie 和 user-agent，复制内容到config.json文件中。
![图片](https://user-images.githubusercontent.com/68672834/187065340-3e1c1958-1f70-4e82-bf77-257fe569bd74.png)
![图片](https://user-images.githubusercontent.com/68672834/187065377-950520fd-bb48-43a0-ac18-2a852e848e48.png)

#### 5. 在json文件中设置最大页数和关键字，运行。


## 示例结果

#### 1. 京东商品信息
![图片](https://user-images.githubusercontent.com/68672834/187065604-cb3e28cb-8f66-4f77-99d1-2ac23bda0b10.png)

#### 2. 网址/微博关键字
![图片](https://user-images.githubusercontent.com/68672834/187065644-fe02da8a-0414-4419-9c51-010ae98dadc1.png)
![图片](https://user-images.githubusercontent.com/68672834/187065617-0d1f76f4-311f-4c4d-8cb3-9431d093ada8.png)
