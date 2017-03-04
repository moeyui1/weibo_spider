# encoding=utf-8
import pymongo
from .items import InformationItem, TweetsItem, FollowsItem, FansItem


class MongoDBPipleline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client["Sina"]
        self.Information = db["Information"]
        self.Tweets = db["Tweets"]
        self.Follows = db["Follows"]
        self.Fans = db["Fans"]
        self.gov=db["Gov"]
        self.users=db['Users']

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, InformationItem):
            try:
                # if item["type"]!="gov":
                #     self.Information.save(dict(item))
                # else:
                #     self.gov.save(dict(item))
                self.users.save(dict(item))

            except Exception:
                pass
        elif isinstance(item, TweetsItem):
            try:
                self.Tweets.save(dict(item))
            except Exception:
                pass
        elif isinstance(item, FollowsItem):
            followsItems = dict(item)
            follows = followsItems.pop("follows")
            for i in range(len(follows)):
                followsItems[str(i + 1)] = follows[i]
            try:
                self.Follows.save(followsItems)
            except Exception:
                pass
        elif isinstance(item, FansItem):
            fansItems = dict(item)
            fans = fansItems.pop("fans")
            for i in range(len(fans)):
                fansItems[str(i + 1)] = fans[i]
            try:
                self.Fans.save(fansItems)
            except Exception:
                pass
        return item
