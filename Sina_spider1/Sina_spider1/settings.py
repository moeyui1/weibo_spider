# -*- coding: utf-8 -*-
import datetime
BOT_NAME = 'Sina_spider1'

NOW=datetime.datetime.now().replace(month=1,day=1)

SPIDER_MODULES = ['Sina_spider1.spiders']
NEWSPIDER_MODULE = 'Sina_spider1.spiders'

DOWNLOADER_MIDDLEWARES = {
    "Sina_spider1.middleware.UserAgentMiddleware": 401,
    "Sina_spider1.middleware.CookiesMiddleware": 402,
# 'scrapy_splash.SplashCookiesMiddleware': 723,
#     'scrapy_splash.SplashMiddleware': 725,
#     'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

ITEM_PIPELINES = {
    'Sina_spider1.pipelines.MongoDBPipleline': 300,
}

# DOWNLOAD_DELAY = 1  # 间隔时间
CONCURRENT_ITEMS = 10000
CONCURRENT_REQUESTS = 1000
# REDIRECT_ENABLED = False
CONCURRENT_REQUESTS_PER_DOMAIN = 100
# CONCURRENT_REQUESTS_PER_IP = 0
# CONCURRENT_REQUESTS_PER_SPIDER=100
# DNSCACHE_ENABLED = True
# LOG_LEVEL = 'INFO'    # 日志级别
# CONCURRENT_REQUESTS = 70
