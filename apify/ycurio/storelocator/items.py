# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class laparrillaItem(scrapy.Item):
    # define the fields for your item here like:
    locator_domain = scrapy.Field()
    location_name = scrapy.Field()
    street_address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zip = scrapy.Field()
    country_code = scrapy.Field()
    store_number = scrapy.Field()
    phone = scrapy.Field()
    location_type = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    hours_of_operation = scrapy.Field()
