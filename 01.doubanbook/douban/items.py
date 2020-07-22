# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class DoubanItem(Item):
    collection = 'books'
    book_info = Field()
    rating_num = Field()
    rating_people = Field()
    ISBN = Field()
    book_name = Field()
    tag = Field()
    book_img = Field()

