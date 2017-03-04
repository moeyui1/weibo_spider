# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
import xlrd
import scrapy
from scrapy.selector import Selector
from ..items import InformationItem


class Spider2(CrawlSpider):
    name = "testSpider"
    host = "http://weibo.com"
    list = []
    error_list = []

    def init_data(self, filename):
        namelist = []
        wb = xlrd.open_workbook(filename)  # 打开文件
        sh = wb.sheet_by_index(0)
        try:
            for i in range(1, 1000):  # 跳过标题头
                list = sh.row_values(i)
                namelist.append(list[0])
        except:
            print(len(namelist))
        return namelist

    def start_requests(self):
        for i in self.init_data('./组织及个人统计2.0.xls'):
            yield scrapy.FormRequest("http://weibo.cn/search/", callback=self.parse, method='POST',
                                     meta={'keyword': i.strip(), 'type': "people"},
                                     formdata={'keyword': i.strip(), 'suser': "找人"})
        for i in self.init_data('./政府部门兼容版2.1.xls'):
            yield scrapy.FormRequest("http://weibo.cn/search/", callback=self.parse, method='POST',
                                     meta={'keyword': i.strip(), 'type': "gov"},
                                     formdata={'keyword': i.strip(), 'suser': "找人"})


    def parse(self, response):
        i = InformationItem()
        i['NickName'] = response.meta['keyword']
        i['type'] = response.meta["type"]
        s = Selector(response)
        url = s.xpath("/html/body/table/tr/td[2]/a[text()=\""+i['NickName']+"\"]/@href").extract_first()

        if url == None:
            self.error_list.append(response.meta['keyword'])
            i['_id'] = response.meta['keyword']
        else:
            if url.startswith('/u/'):
                str = url[3:url.find("?")]
            else:
                str = url[1:url.find("?")]
            self.list.append(str)
            i["idname"] = str
            i['_id'] = response.meta['keyword'] + i['idname']
            yield i

    def close(spider, reason):
        # print(spider.list)
        print('error_list:',spider.error_list)
