import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pelicanstatecu_com')


crawled = []
class Scrape(base.Spider):

    def get_id_from_link(self, link):
        link = link.split('id=')[1]
        link = link[:link.find('&')]
        return link

    def crawl(self):
        base_url = "https://www.pelicanstatecu.com/about-us/locations-hours.html"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//li[@class="loc"]'):
            i = base.Item(href)
            name = href.xpath('./@data-title')[0]
            if name not in crawled:
                i.add_value('location_name', name, lambda x: x.strip())
                i.add_value('locator_domain', base_url)
                i.add_xpath('page_url', './/a[@class="seeDetails"]/@href', base.get_first, lambda x: urljoin(base_url, x))
                hours = ""
                t1 = href.xpath('.//div[@class="lobbyHours" or @class="driveThroughHours"]/h5')
                if t1:
                    for t in t1:
                        hours+=t.xpath('./text()')[0]
                        hours+=': '
                        hours+=': '.join(t.xpath('./following-sibling::div[1]/span/text()'))
                        hours+=';'
                if hours:
                    i.add_value('hours_of_operation', hours)
                i.add_xpath('latitude', './@data-latitude', base.get_first)
                i.add_xpath('longitude', './@data-longitude', base.get_first)
                i.add_xpath('street_address', './@data-address1 | ./@data-address2', lambda x: ', '.join([s for s in x if s.strip()]))
                i.add_xpath('city', './@data-city', base.get_first)
                i.add_xpath('state', './@data-state', base.get_first)
                i.add_xpath('zip', './@data-zip', base.get_first)
                i.add_xpath('phone', './/div[@class="contact"]//div[span="Phone"]/span[@class="value"]/text()', base.get_first)
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                i.add_value('store_number', self.get_id_from_link(i.as_dict()['page_url']))
                crawled.append(name)
                yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
