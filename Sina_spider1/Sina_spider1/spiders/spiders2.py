# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
import xlrd
import scrapy
from scrapy.selector import Selector


class Spider2(CrawlSpider):
    name = "testSpider"
    host = "http://weibo.com"
    list=[]
    error_list=[]

    def init_data(self):
        namelist = []
        wb = xlrd.open_workbook('./组织及个人统计.xls')  # 打开文件
        sh = wb.sheet_by_index(0)
        try:
            for i in range(1, 1000):  # 跳过标题头
                list = sh.row_values(i)
                namelist.append(list[0])
        except:
            print('sheet %d the end' % 0)
        return namelist

    def start_requests(self):
        print(self.init_data())
        for i in self.init_data():
            yield scrapy.FormRequest("http://weibo.cn/search/", callback=self.parse, method='POST',meta={'keyword': i},
                          formdata={'keyword': i, 'suser': "找人"})

    def parse(self, response):
        # print(response.body)
        s=Selector(response)
        url=s.xpath("/html/body/table[1]/tr/td[1]/a[1]/@href").extract_first()
        if url==None:
            self.error_list.append(response.meta['keyword'])
        else:
            if url.startswith('/u/'):
                str = url[3:url.find("?")]
            else:
                str = url[1:url.find("?")]
            self.list.append(str)


    def close(spider, reason):
        print(spider.list)
        print(spider.error_list)
