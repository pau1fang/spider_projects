# -*- coding: utf-8 -*-
import scrapy
from anjuke.items import AnjukeItem
from lxml.html import etree
import re


class HouseSpider(scrapy.Spider):
    name = 'house'
    allowed_domains = ['anjuke.com']
    start_urls = ['https://www.anjuke.com/sy-city.html']
    # start_urls = ['https://aq.fang.anjuke.com/loupan/all/p1/']

    def parse(self, response):
        urls = response.xpath('//*[@class="city_list"]/a/@href').extract()
        for url in urls:
            city = re.findall(r'https://(.*?).anjuke.com', url)[0]
            url_fang = f'https://{city}.fang.anjuke.com/loupan/all/p1/'
            yield scrapy.Request(url_fang, callback=self.parse_item)

    def parse_item(self, response):
        item = AnjukeItem()
        infos = response.xpath('//*[@class="infos"]').extract()
        prices = response.xpath('//*[@class="favor-pos"]//span/text()').extract()
        item['city'] = response.xpath('//span[@class="city"]/text()').extract_first()
        for i in range(len(infos)):
            info = etree.HTML(infos[i])
            item['lp_name'] = info.xpath('//*[@class="items-name"]/text()')[0]
            item['address'] = info.xpath('//*[@class="list-map"]/text()')[0].split()[-1]
            item['area'] = info.xpath('//*[@class="building-area"]/text()')[0].split('：')[-1]
            item['price'] = prices[i]
            yield item
        url = response.xpath('//*[@class="next-page next-link"]/@href').extract_first()
        if url:
            yield scrapy.Request(url, callback=self.parse_item)

