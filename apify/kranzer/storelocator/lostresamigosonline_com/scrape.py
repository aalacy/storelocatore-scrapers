import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lostresamigosonline_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "http://lostresamigosonline.com/locations.html"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for s in sel['tree'].xpath('//div[@class="loc2"]'):
            i = base.Item(s)
            i.add_xpath('location_name', './span[@class="tres"]/text()', base.get_first, lambda x: x.strip())
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_xpath('hours_of_operation', './span[@class="horario"]/text()', lambda x: '; '.join(x))
            i.add_xpath('phone', './/span[@class="info"]/text()[2]', base.get_first, lambda x: x.replace('\r', '').replace('\n','').strip())
            loc = s.xpath('.//span[@class="info"]/text()[1]')[0]
            if loc:
                if i.as_dict()['location_name'] != "Canton":
                    tup = re.findall(r'(.+),?\s(.+?),\s([A-Z][A-Z])\s(.+)', loc.replace('\r', '').strip())
                    if tup:
                        i.add_value('street_address', tup[0][0])
                        i.add_value('city', tup[0][1])
                        i.add_value('state', tup[0][2], lambda x: x.upper())
                        i.add_value('zip', tup[0][3])
                        i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                    else:
                        pass
                else:
                    i.add_value('street_address', loc)
                    i.add_value('city', 'Canton')
                    i.add_value('state', 'MI')
                    i.add_value('country_code', 'US')

            i.add_value('latitude', "<INACCESSIBLE>")
            i.add_value('longitude', "<INACCESSIBLE>")
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
