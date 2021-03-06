# -*- coding: utf-8 -*-
import pymongo
from anjuke.items import AnjukeItem


class AnjukePipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[AnjukeItem.collection].create_index([('id', pymongo.ASCENDING)])

    def process_item(self, item, spider):
        self.db[item.collection].insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
