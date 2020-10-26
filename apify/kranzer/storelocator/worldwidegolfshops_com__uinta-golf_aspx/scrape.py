import re
from pprint import pprint
from string import capwords

import base
import json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('worldwidegolfshops_com__uinta-golf_aspx')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.worldwidegolfshops.com/uinta-golf.aspx"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//a[@class="store-name-link"][1]/@href'):
            fs = base.selector(urljoin(base_url,href), headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            s = base.selector(fs['tree'].xpath('//iframe[1]/@src')[0], headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            i = base.Item(s['tree'])
            i.add_xpath('location_name', '//h1[@class="storePageName"]/text()', base.get_first, lambda x: x.strip())
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', s['url'])
            i.add_xpath('hours_of_operation', './/div[@class="hoursRow "]', lambda x: '; '.join([' '.join(s.xpath('.//text()')) for s in x]))
            i.add_xpath('phone', './/span[@id="telephone"]/text()', base.get_first, lambda x: x.replace('\r', '').replace('\n','').strip())
            i.add_xpath('street_address', '//span[@id="address"]/span[@itemprop="streetAddress"]/text()', base.get_first)
            i.add_xpath('city', '//span[@id="address"]/span[@itemprop="addressLocality"]/text()', base.get_first)
            i.add_xpath('zip', '//span[@id="address"]/span[@itemprop="postalCode"]/text()', base.get_first)
            i.add_xpath('state', '//span[@id="address"]/span[@itemprop="addressRegion"]/text()', base.get_first)

            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))

            js = s['tree'].xpath('//script/text()[contains(., "LatLng")]')[0]
            try:
                i.add_value('latitude', re.findall(r'LatLng\((.+?),\s(.+?)\)', js)[0][0])
                i.add_value('longitude', re.findall(r'LatLng\((.+?),\s(.+?)\)', js)[0][1])
            except:
                pass
            logger.info(i)
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
