# 新浪微博爬虫 demo

这是一个基于`Scrapy`开发，爬取新浪微博环境相关微博内容，并存储到本地 MongoDB 中的爬虫 DEMO。

## Feature

### Cookies 中间件

为了应对微博的反爬虫机制，实现了自动轮换多组预设账号 Cookies 的中间件。从[新浪通行证处](https://login.sina.com.cn)登录，绕过验证码等麻烦问题。

### UserAgent 中间件

目的同上，多组轮换。

### 集成 MongoDB

实现了一个 MongoDB 的 Pipleline。

## 使用

运行环境为 Python3.5。

`spiders`目录下有3个 spider ，

+ `sinaSpider`: 爬取数据库Users表中用户的用户信息
+ `testSpider`: 爬取本地 xls 表格中用户的用户信息
+ `pageSpider`: 根据`settings.py`中的时间范围爬取数据库中用户的历史微博数据

在`cookies.py`中可自定义爬取用的微博账号。