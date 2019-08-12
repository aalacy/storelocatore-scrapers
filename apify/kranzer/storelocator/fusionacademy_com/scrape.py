import re
import time
from string import capwords

import usaddress
from lxml import html
import base
import requests, json
from urllib.parse import urljoin

base_url = "https://www.fusionacademy.com/locations/"


class Scrape(base.Spider):

    def crawl(self):
        for store in html.fromstring(requests.get(base_url).text).xpath('//div[@class="location-block__card"]'):
            i = base.Item(store)
            i.add_value('locator_domain', urljoin(base_url, store.xpath('./a[@class="location-block__card--link"]/@href')[0]))
            i.add_xpath('location_name', './h6/text()', base.get_first, lambda x: x.strip())
            addr = store.xpath('./p/text()')
            addr = [s.replace("District of Columbia", 'DC') for s in addr]
            if len(addr) == 3:
                i.add_value('street_address', ', '.join(addr[:2]), lambda x: x.replace('\n','').replace(', , ',', '))
                st = addr[2]
                i.add_value('city', st[:st.find(',')], lambda x: x.replace('\n',''))
                st = st[st.find(',')+2:]
                i.add_value('state', st.split(' ')[0], lambda x: x.replace('\n',''))
                try:
                    i.add_value('zip', st.split(' ')[1], lambda x: x.replace('\n',''))
                except:
                    pass
            elif len(addr) == 2:
                i.add_value('street_address', addr[0])
                st = addr[1]
                i.add_value('city', st[:st.find(',')], lambda x: x.replace('\n',''))
                st = st[st.find(',') + 2:]
                i.add_value('state', st.split(' ')[0], lambda x: x.replace('\n',''))
                try:
                    i.add_value('zip', st.split(' ')[1], lambda x: x.replace('\n',''))
                except:
                    pass
            elif len(addr) == 1:
                st = addr[0]
                i.add_value('city', st[:st.find(',')], lambda x: x.replace('\n',''))
                st = st[st.find(',') + 2:]
                i.add_value('state', st.split(' ')[0], lambda x: x.replace('\n',''))
                try:
                    i.add_value('zip', st.split(' ')[1], lambda x: x.replace('\n',''))
                except:
                    pass
            i.add_xpath('phone', './/a[contains(@href, "tel")]/text()', base.get_first)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            print(i)
            yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
