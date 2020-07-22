# -*- coding: utf-8 -*-
import scrapy
from douban.items import DoubanItem
import re
from scrapy.http import Request
from urllib.parse import urljoin


class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['book.douban.com']
    start_urls = ['https://book.douban.com/tag/?view=cloud']

    def parse(self, response):
        # get item urls and yield requests
        tag_selector = response.xpath('//*[@class="tagCol"]//a/@href').extract()
        for tag in tag_selector:
            yield Request(urljoin(response.url, tag))
        next_selector = response.xpath('//*[@id="subject_list"]//*[@rel="next"]/@href').extract_first()
        if next_selector:
            yield Request(urljoin(response.url, next_selector))
        item_selector = response.xpath('//*[@id="subject_list"]//li[1]//*[@class="nbg"]/@href').extract()
        if item_selector:
            for url in item_selector:
                yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        item = DoubanItem()
        doc = response.xpath('//div[@id="info"]').extract_first()
        if doc:
            doc = doc.replace('\n', '').replace(' ', '').replace('</a>', '')
        spans = doc.split('<br>')
        book_info = {}
        for span in spans:
            if re.findall('span', span):
                if re.findall('span', span).__len__() < 4:
                    message_key = re.findall('pl\">(.*?)<.*>(.*)', span)[0][0].replace(':', '').strip()
                    message_value = re.findall('pl\">(.*?)<.*>(.*)', span)[0][1]
                    if message_key != 'ISBN':
                        book_info[message_key] = message_value
                    else:
                        item['ISBN'] = message_value
                else:
                    message_key = re.findall('pl\">(.*?)<.*>(.*?)<.*', span)[0][0].replace(':', '').strip()
                    message_value = re.findall('pl\">(.*?)<.*>(.*?)<.*', span)[0][1]
                    book_info[message_key] = message_value
        item['book_info'] = book_info
        item['rating_num'] = response.xpath('//*[@class="rating_self clearfix"]/strong[1]/text()').extract_first().strip()
        item['rating_people'] = response.xpath('//*[@class="rating_self clearfix"]//*[@property="v:votes"][1]/text()').extract_first()
        item['book_name'] = response.xpath('//*[@property="v:itemreviewed"]/text()').extract_first()
        item['tag'] = response.xpath('//*[@id="db-tags-section"]//span/a/text()').extract()
        item['book_img'] = response.xpath('//*[@id="mainpic"]/a/img/@src').extract_first()
        yield item


