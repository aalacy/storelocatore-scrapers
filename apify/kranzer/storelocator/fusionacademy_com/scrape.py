import re
import time
from string import capwords

import usaddress
from lxml import html
import base
import requests, json
from urllib.parse import urljoin
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fusionacademy_com')






class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.fusionacademy.com/campuses/"
        r = requests.get(base_url, headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"})
        for store in html.fromstring(r.text).xpath('//div[@class="location-block__card"]'):
            i = base.Item(store)
            i.add_value('locator_domain', urljoin(base_url, store.xpath('./a[@class="location-block__card--link"]/@href')[0]))
            i.add_xpath('location_name', './h6/text()', base.get_first, lambda x: x.strip())
            addr = store.xpath('./p/text()')
            addr = [s.replace("District of Columbia", 'DC') for s in addr]
            if len(addr) == 3:
                i.add_value('street_address', ', '.join(addr[:2]), lambda x: x.replace('\n','').replace(', , ',', '), lambda x: x.replace('\r', ''))
                st = addr[2]
                i.add_value('city', st[:st.find(',')], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                st = st[st.find(',')+2:]
                i.add_value('state', st.split(' ')[0], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                try:
                    i.add_value('zip', st.split(' ')[1], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                except:
                    pass
            elif len(addr) == 2:
                i.add_value('street_address', addr[0])
                st = addr[1]
                i.add_value('city', st[:st.find(',')], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                st = st[st.find(',') + 2:]
                i.add_value('state', st.split(' ')[0], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                try:
                    i.add_value('zip', st.split(' ')[1], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                except:
                    pass
            elif len(addr) == 1:
                st = addr[0]
                i.add_value('city', st[:st.find(',')], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                st = st[st.find(',') + 2:]
                i.add_value('state', st.split(' ')[0], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                try:
                    i.add_value('zip', st.split(' ')[1], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                except:
                    pass
            elif len(addr) == 4:
                i.add_value('street_address', ', '.join(addr[:3]), lambda x: x.replace('\n','').replace(', , ',', '), lambda x: x.replace('\r', ''))
                st = addr[3]
                i.add_value('city', st[:st.find(',')], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                st = st[st.find(',')+2:]
                i.add_value('state', st.split(' ')[0], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                try:
                    i.add_value('zip', st.split(' ')[1], lambda x: x.replace('\n',''), lambda x: x.replace('\r', ''))
                except:
                    pass
            i.add_xpath('phone', './/a[contains(@href, "tel")]/text()', base.get_first)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            logger.info(i)
            yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
