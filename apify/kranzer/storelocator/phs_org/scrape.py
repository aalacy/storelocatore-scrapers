import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('phs_org')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.phs.org/hospitals/Pages/default.aspx"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//div[contains(@class, "hospitals_col")]//li[strong/a/@href]'):
            hs = base.selector(urljoin(base_url, href.xpath('./strong/a/@href')[0]), headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            i = base.Item(hs['tree'])
            i.add_value('location_name', href.xpath('./strong/a/text()')[0])
            i.add_value('locator_domain', sel['url'])
            i.add_value('page_url', hs['url'])
            i.add_xpath('phone', './/div[@class="pageIntro__phone"]//a/text()', lambda x: [s for s in x if s], lambda x: base.get_first(x))
            i.add_xpath('street_address', './/div[@class="pageIntro__address"]/a/span[1]/text()', base.get_first)
            i.add_xpath('city', '//div[@class="pageIntro__address"]/a/span[2]//text()', lambda x: ''.join(x), lambda x: x.replace('\r','').replace('\n', '').strip()[:x.find(',')] if ',' in x else x)
            i.add_xpath('state', '//div[@class="pageIntro__address"]/a/span[2]//text()', lambda x: ''.join(x), lambda x: x.replace('\r','').replace('\n', '').strip()[x.find(',')+1:].strip() if ',' in x else x)
            i.add_value('zip', href.xpath('./p/text()[2]'), base.get_first, lambda x: re.findall(r'\d{5}', x), lambda x: base.get_first(x))
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
