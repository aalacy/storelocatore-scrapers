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
        base_url = "https://playntrade.ca/en/store-locator/"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//div[contains(@class,"map-store-item")]'):
            i = base.Item(href)
            i.add_xpath('location_name', './h2/a/text()', base.get_first, lambda x: x.strip())
            i.add_value('locator_domain', base_url)
            i.add_xpath('page_url', './h2/a/@href', base.get_first, lambda x: urljoin(base_url, x))
            i.add_xpath('hours_of_operation', './/div[@class="map-store-hours"]/p/text()', lambda x: '; '.join([s.replace('\n','') for s in x]), lambda x: x.replace('Heure d’ouverture :;', '').strip())
            i.add_xpath('phone', './/div[@class="map-store-tel"]/a/text()', base.get_first)
            loc = href.xpath('.//div[@class="map-store-address"]/text()[2]')[0]
            if loc:
                tup = re.findall(r'(.+),\s(.+?),\s([A-Z][A-Z])\s(.+)', loc.replace('\r', '').strip())
                if tup:
                    i.add_value('street_address', tup[0][0])
                    i.add_value('city', tup[0][1])
                    i.add_value('state', tup[0][2], lambda x: x.upper())
                    i.add_value('zip', tup[0][3])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                else:
                    tup = re.findall(r'(.+),\s(Sherbrooke),\s(.+)', loc.replace('\r', '').strip())
                    if tup:
                        i.add_value('street_address', tup[0][0])
                        i.add_value('city', tup[0][1])
                        i.add_value('state', "QC")
                        i.add_value('zip', tup[0][2], lambda x: x.upper())
                        i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            next_sel = base.selector(i.as_dict()['page_url'])
            try:
                i.add_value('latitude', next_sel['tree'].xpath('.//div[@class="marker"]/@data-lat'), base.get_first)
                i.add_value('longitude', next_sel['tree'].xpath('.//div[@class="marker"]/@data-lng'), base.get_first)
            except:
                pass
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
