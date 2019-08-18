import re
import time
from string import capwords

import usaddress
from lxml import html
import base
import requests, json
from urllib.parse import urljoin

base_url = "https://www.drbdiet.com/weight-loss-clinics/"


class Scrape(base.Spider):

    def crawl(self):
        for store in html.fromstring(requests.get(base_url).text).xpath('//ul[contains(@class, "locations")]//a/@href[not(contains(., "-loss-clinics"))]'):
            store_selector = base.selector(store)
            i = base.Item(store_selector['tree'])
            i.add_value('locator_domain', store_selector['url'])
            i.add_xpath('hours_of_operation', '//div[@class="wpsl-hours-details"]//text()[not(parent::h3)]', lambda x: [s_.strip() for s_ in x if s_],lambda x: '; '.join([' '.join(x) for x in zip(x[0::2], x[1::2])]).replace('\n', '').strip(), lambda x: x[2:] if x.startswith('; ') else x)
            i.add_xpath('location_name', '//div[contains(@class, "clinic-details")]/strong/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('street_address', '//div[contains(@class, "clinic-details")]/div/span[@itemprop="streetAddress"]/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('city', '//div[contains(@class, "clinic-details")]/div/span[@itemprop="addressLocality"]/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('state', '//div[contains(@class, "clinic-details")]/div/span[@itemprop="addressRegion"]/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('zip', '//div[contains(@class, "clinic-details")]/div/span[@itemprop="postalCode"]/text()', base.get_first, lambda x: x.strip(), lambda x: x[:3]+' '+x[3:] if ' ' not in x else x)
            i.add_xpath('phone', '//div[@class="wpsl-contact-details"]//span[@itemprop="telephone"]/text()', base.get_first)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            lat_lng_st = store_selector['tree'].xpath('//script[@type="text/javascript"]/text()[contains(., "wpslMap_0")]')[0]
            if lat_lng_st:
                lat_lng_st = lat_lng_st[lat_lng_st.find('wpslMap_0'):]
                lat_lng = re.findall(r'\"lat\":\"(?P<lat>.+?)\",\"lng\":\"(?P<lng>.+?)\"', lat_lng_st)
                if lat_lng:
                    i.add_value('latitude', lat_lng[0][0])
                    i.add_value('longitude', lat_lng[0][1])
            yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
