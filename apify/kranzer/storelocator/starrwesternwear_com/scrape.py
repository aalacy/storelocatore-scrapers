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
        base_url = "https://starrwesternwear.com/contact-us"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//p[strong][preceding-sibling::h2[1][contains(text(), "Stores")]]'):
            texts = [s.strip() for s in href.xpath('./text()') if s.strip()]
            i = base.Item(href)
            i.add_xpath('location_name', './strong/text()', base.get_first, lambda x: x.strip())
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_value('hours_of_operation', texts, lambda x: ', '.join(x[1:]))
            i.add_xpath('phone', './a[contains(@href, "tel")]/text()', base.get_first)
            loc = texts[0]
            if loc:
                tup = re.findall(r'(.+?),\s(.+)\s(.+?),?\s(\d+)', loc.replace('\r', '').strip())
                if tup:
                    i.add_value('street_address', tup[0][0])
                    i.add_value('city', tup[0][1])
                    i.add_value('state', tup[0][2], lambda x: base.get_state_code(x))
                    i.add_value('zip', tup[0][3])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
