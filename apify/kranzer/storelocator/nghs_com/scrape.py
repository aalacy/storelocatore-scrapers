import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nghs_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.nghs.com/our-locations"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//ul[contains(@class, "hospitals")]/li/a/@href'):
            hs = base.selector(urljoin(base_url, href), headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            i = base.Item(hs['tree'])
            i.add_xpath('location_name', './/div[contains(@class, "page-heading-title")]/text()', base.get_first, lambda x: x.strip())
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', hs['url'])
            i.add_xpath('phone', '//div[@class="page-heading"]//a[@class="location-phone"]/@href', lambda x: [s for s in x if s], lambda x: base.get_first(x).replace('tel:',''))
            i.add_xpath('street_address', '//div[contains(@class, "location-address")]/a/text()[1]', base.get_first)
            loc = [s.replace('\n', '').replace('\r', '').strip() for s in
                   hs['tree'].xpath('.//div[contains(@class, "location-address")]/a/text()[2]') if s.replace('\n', '').replace('\r', '').strip()]

            if loc:
                tup = re.findall(r'(.+?),?\s([A-Z]+|California),?\s(\d+)', loc[-1].replace('\r', '').strip())
                if tup:
                    i.add_value('city', tup[0][0])
                    i.add_value('state', tup[0][1])
                    i.add_value('zip', tup[0][2])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_value('latitude', '<INACCESSIBLE>')
            i.add_value('longitude', '<INACCESSIBLE>')
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
