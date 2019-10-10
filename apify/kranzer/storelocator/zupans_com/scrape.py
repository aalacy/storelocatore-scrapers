import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.zupans.com/stores/"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//a[contains(@class, "store-splash")]/@href[contains(., "stores")]'):
            s = base.selector(href, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            i = base.Item(s['tree'])
            i.add_xpath('location_name', './/header/h1[contains(@class, "block-title")]/text()', base.get_first, lambda x: x.strip())
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', s['url'])
            i.add_xpath('hours_of_operation', './/p/text()[contains(., "Store Hours")]', base.get_first, lambda x: x.replace('Store Hours: ', '').strip())
            i.add_xpath('phone', './/div[@class="map-location"]/p/a[contains(@href, "tel")]/text()', base.get_first)
            i.add_xpath('street_address', '//div[@class="map-location"]/address/span[@itemprop="streetAddress"]/text()', base.get_first)
            i.add_xpath('city', '//div[@class="map-location"]/address/span[@itemprop="addressLocality"]/text()', base.get_first)
            i.add_xpath('zip', '//div[@class="map-location"]/address/span[@itemprop="postalCode"]/text()', base.get_first)
            i.add_xpath('state', '//div[@class="map-location"]/address/span[@itemprop="addressRegion"]/text()', base.get_first)

            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))

            js = s['tree'].xpath('//div[@class="map-location"]/a/@href')[0]
            try:
                i.add_value('latitude', js[js.find('@')+1:].split(',')[0])
                i.add_value('longitude', js[js.find('@')+1:].split(',')[1])
            except:
                pass
            print(i)
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
