# -*- coding: utf-8 -*-
from scrapy import cmdline

cmdline.execute("scrapy crawl sinaSpider ".split())
# cmdline.execute("scrapy crawl sinaSpider -s JOBDIR=crawls/sinaSpider-1".split())
# cmdline.execute("scrapy crawl testSpider".split())
# cmdline.execute("scrapy crawl pageSpider".split())

