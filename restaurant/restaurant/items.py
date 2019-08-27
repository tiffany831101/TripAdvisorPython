# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TripadvisorItem(scrapy.Item):
    title = scrapy.Field()
    res_type = scrapy.Field()
    rating_count=scrapy.Field()
    info_url =scrapy.Field()
    cellphone = scrapy.Field()
    address = scrapy.Field()
    street = scrapy.Field()
    rating= scrapy.Field()
    comment = scrapy.Field()
    open_time = scrapy.Field()
    pass

class HotelItem(scrapy.Item):
    title = scrapy.Field()
    comment_count=scrapy.Field()
    star =scrapy.Field()
    city = scrapy.Field()
    address = scrapy.Field()
    cellphone = scrapy.Field()
    intro= scrapy.Field()
    tourist = scrapy.Field()
    comment = scrapy.Field()
    pass