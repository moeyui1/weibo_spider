# -*- coding: utf-8 -*-
import re
import datetime
import logging

import pymongo
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from ..items import InformationItem, TweetsItem, FollowsItem, FansItem


class Spider(CrawlSpider):
    name = "pageSpider"
    host = "http://weibo.cn"
    start_urls = []
    scrawl_ID = set(start_urls)  # 记录待爬的微博ID
    finish_ID = set()  # 记录已爬的微博ID

    def start_requests(self):
        db = pymongo.MongoClient("localhost", 27017)['Sina']
        url_tweets = "http://weibo.cn/%s?page=1800"
        list = []
        for i in db['Users'].find({}):
            list.append(i['idname'])
        for inf in db['Information'].find({"idname": {'$ne': None}}):
            if inf['idname'] in list:
                continue
            yield Request(url=url_tweets % inf['idname'],
                          meta={"ID": inf['idname'], "type": 'people', "username": inf['NickName'], 'obj': inf,
                                'page': 1800},
                          callback=self.parse2)  # 去爬微博
        for g_inf in db['Gov'].find({"idname": {'$ne': None}}):
            if g_inf['idname'] in list:
                continue
            yield Request(url=url_tweets % g_inf['idname'],
                          meta={"ID": g_inf['idname'], "type": 'gov', "username": g_inf['NickName'], 'obj': g_inf,
                                'page': 1800},
                          callback=self.parse2)  # 去爬微博

    def parse0(self, response):
        """ 抓取个人信息1 """
        informationItems = InformationItem()
        selector = Selector(response)
        text0 = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').extract_first()
        if text0:
            num_tweets = re.findall(u'\u5fae\u535a\[(\d+)\]', text0)  # 微博数
            num_follows = re.findall(u'\u5173\u6ce8\[(\d+)\]', text0)  # 关注数
            num_fans = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text0)  # 粉丝数
            if num_tweets:
                informationItems["Num_Tweets"] = int(num_tweets[0])
            if num_follows:
                informationItems["Num_Follows"] = int(num_follows[0])
            if num_fans:
                informationItems["Num_Fans"] = int(num_fans[0])
            informationItems["_id"] = response.meta["ID"]
            url_information1 = "http://weibo.cn/%s/info" % response.meta["ID"]
            # yield Request(url=url_information1, meta={"item": informationItems}, callback=self.parse1)

    def parse1(self, response):
        """ 抓取个人信息2 """
        informationItems = response.meta["item"]
        selector = Selector(response)
        text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())  # 获取标签里的所有text()
        nickname = re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1)  # 昵称
        gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)  # 性别
        place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # 地区（包括省份和城市）
        signature = re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?);', text1)  # 个性签名
        birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1)  # 生日
        sexorientation = re.findall(u'\u6027\u53d6\u5411[:|\uff1a](.*?);', text1)  # 性取向
        marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?);', text1)  # 婚姻状况
        url = re.findall(u'\u4e92\u8054\u7f51[:|\uff1a](.*?);', text1)  # 首页链接

        if nickname:
            informationItems["NickName"] = nickname[0]
        if gender:
            informationItems["Gender"] = gender[0]
        if place:
            place = place[0].split(" ")
            informationItems["Province"] = place[0]
            if len(place) > 1:
                informationItems["City"] = place[1]
        if signature:
            informationItems["Signature"] = signature[0]
        if birthday:
            try:
                birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                informationItems["Birthday"] = birthday - datetime.timedelta(hours=8)
            except Exception:
                pass
        if sexorientation:
            if sexorientation[0] == gender[0]:
                informationItems["Sex_Orientation"] = "gay"
            else:
                informationItems["Sex_Orientation"] = "Heterosexual"
        if marriage:
            informationItems["Marriage"] = marriage[0]
        if url:
            informationItems["URL"] = url[0]
        yield informationItems

    def parse2(self, response):
        """ 抓取微博数据 """
        should_continue = True

        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')
        for tweet in tweets:
            tweetsItems = TweetsItem()
            id = tweet.xpath('@id').extract_first()  # 微博ID

            others = tweet.xpath('div/span[@class="ct"]/text()').extract_first()  # 求时间和使用工具（手机或平台）

            if others:
                others = others.split(u"\u6765\u81ea")
                tweetsItems["PubTime"] = self.time_handler(others[0].strip())
                if (tweetsItems["PubTime"] < self.settings["START_TIME"] - datetime.timedelta(days=365)):
                    should_continue = False
                    break  # 不需要晚于时间范围的数据，直接跳出
                elif (tweetsItems["PubTime"] > self.settings["START_TIME"]):
                    continue  # 早于时间范围的数据，跳过此次循环
                if len(others) == 2:
                    tweetsItems["Tools"] = others[1]

            print(tweetsItems["PubTime"])
            obj = response.meta['obj']
            obj['Start_page'] = response.meta['page']
            inf = InformationItem()
            inf['_id'] = obj.get("_id").strip()
            inf['NickName'] = obj.get("NickName").strip()
            inf['Start_page'] = obj.get("Start_page")
            inf['type'] = obj.get("type")
            inf['idname'] = obj.get("idname").strip()
            should_continue = False
            yield inf
            break
            # yield tweetsItems
        url_next = selector.xpath(
            u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

        if url_next and should_continue and response.meta['page'] < 2000:
            yield Request(url=self.host + "/%s?page=%d" % (response.meta['obj']['idname'], response.meta['page'] + 1),
                          meta={
                              "ID": response.meta["ID"],
                              "type": response.meta["type"],
                              "username": response.meta["username"],
                              'obj': response.meta['obj'],
                              'page': response.meta['page'] + 1
                          }, callback=self.parse2)
        else:
            if not response.meta.get("retry"):
                yield Request(url=self.host + "/%s?page=%d" % (response.meta['obj']['idname'], response.meta['page']),
                              meta={
                                  "ID": response.meta["ID"],
                                  "type": response.meta["type"],
                                  "username": response.meta["username"],
                                  'obj': response.meta['obj'],
                                  'page': response.meta['page'],
                                  'retry': True
                              }, callback=self.parse2)
            else:
                print(should_continue, "no more pages---------")

    def time_handler(self, str):
        n = self.settings['NOW']

        if str.find("今天") != -1:
            t = re.findall("[0-9]{2}", str)
            return n.replace(hour=int(t[0]), minute=int(t[1]))
        elif (str.find("月") != -1):
            t = re.findall("[0-9]{2}", str)
            return n.replace(month=int(t[0]), day=int(t[1]), hour=int(t[2]), minute=int(t[3]))
        elif (str.find("-") != -1):
            y = re.findall("[0-9]{4}", str)
            t = re.findall("[0-9]{2}", str[4:])
            return n.replace(year=int(y[0]), month=int(t[0]), day=int(t[1]), hour=int(t[2]), minute=int(t[3]),
                             second=int(t[4]))
        else:
            return n
