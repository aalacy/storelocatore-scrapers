import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nailsplusspa_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.nailsplusspa.com/locations"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//div[contains(@class, "sqs-col")]/div[contains(@class, "sqs-row")]'):
            i = base.Item(href)
            i.add_xpath('location_name', './/div[@class="sqs-block-content"]/p[1]/strong/text()', base.get_first, lambda x: x.strip())
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_xpath('hours_of_operation', './/div[@class="sqs-block-content"]/p[2]/text()', lambda x: '; '.join([s.replace('\n','') for s in x]), lambda x: x.replace('—;','').strip())
            i.add_xpath('phone', './/div[@class="sqs-block-content"]/p[2]/strong/text()[contains(., "tel. ")]', base.get_first, lambda x: x.replace('tel. ', ''))
            i.add_xpath('street_address', './/div[@class="sqs-block-content"]/p[1]/text()[1]', base.get_first)
            loc = href.xpath('.//div[@class="sqs-block-content"]/p[1]/text()[2]')[0]
            if loc:
                tup = re.findall(r'(.+?),\s([A-Z][A-Z])\s(.+)', loc.replace('\r', '').strip())
                if tup:
                    i.add_value('city', tup[0][0])
                    i.add_value('state', tup[0][1], lambda x: x.upper())
                    i.add_value('zip', tup[0][2])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            js = href.xpath('.//div[contains(@class, "sqs-block-map")]/@data-block-json')[0]
            try:
                i.add_value('latitude', json.loads(js)['location']['markerLat'])
                i.add_value('longitude', json.loads(js)['location']['markerLng'])
            except:
                pass
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
