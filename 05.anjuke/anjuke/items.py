# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AnjukeItem(scrapy.Item):
    collection = 'house'
    city = scrapy.Field()
    lp_name = scrapy.Field()
    address = scrapy.Field()
    area = scrapy.Field()
    price = scrapy.Field()
