# -*- coding: utf-8 -*-
import scrapy
import re
from restaurant.items import HotelItem
class HotelSpider(scrapy.Spider):
    name = 'hotel'
    allowed_domains = ['www.tripadvisor.com.tw']
    start_urls = ['https://www.tripadvisor.com.tw/Hotels-g293913-Taipei-Hotels.html','https://www.tripadvisor.com.tw/Hotels-g1432365-New_Taipei-Hotels.html']

    def parse(self, response):
        item_urls = response.xpath('//div[@class="listing_title"]/a/@href').getall()
        
        for item_url in item_urls[1:]:
            print("準備抓取%s"% item_url)
            yield scrapy.Request(url = response.urljoin(item_url), callback=self.parse_info)

        next_url = response.xpath('//a[@class="nav next taLnk ui_button primary"]/@href').get()
        if next_url:
            yield scrapy.Request(url = response.urljoin(next_url), callback=self.parse)
    def parse_info(self, response):
        item = HotelItem()
        title = response.xpath('//h1[@id="HEADING"]/text()').get()
        comment_count = response.xpath('//span[@class="reviewCount ui_link level_4"]/text()').get()
        if comment_count:
            comment_count =comment_count.split('\xa0')[0].split(",")
            comment_count = int("".join(comment_count))
        else:
            comment_count = 0
        comment_count = int(comment_count)
        star = response.xpath('//span[@class="hotels-hotel-review-about-with-photos-Reviews__overallRating--vElGA"]/text()').get()
        if star:
            star = float(star)
        else:
            star = 0
        city = response.xpath('//span[@class="locality"]/text()').get()
        address = response.xpath('//span[@class="street-address"]/text()').get()
        cellphone = response.xpath('//span[@class="detail  ui_link level_4 is-hidden-mobile"]/text()').get()
        intro = response.xpath('//div[@class="common-text-ReadMore__content--2X4LR"]/text()').get()
        tourist_info = response.xpath('//div[@class="ui_column is-4 hotels-hotel-review-location-layout-LocationColumn__locationColumn--kANeS"]')
        for info in tourist_info[2:]:
            tourist = info.xpath('.//div[@class="hotels-hotel-review-location-NearbyLocation__name--1pAvV"]/text()').getall()
            tourist = ",".join(tourist)
        comment = response.xpath('//q[@class="hotels-review-list-parts-ExpandableReview__reviewText--3oMkH"]/span/text()').getall()
        comment = ",".join(comment)
        item=HotelItem(title=title,comment_count=comment_count,star=star,city=city,address=address,intro=intro,cellphone=cellphone,tourist=tourist,comment=comment)
        yield item

