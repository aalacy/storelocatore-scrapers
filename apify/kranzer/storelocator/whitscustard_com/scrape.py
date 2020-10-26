import re
import time
from string import capwords

import usaddress
from lxml import html
import base
import requests, json
from urllib.parse import urljoin
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('whitscustard_com')



base_url = "https://www.whitscustard.com/locations"


class Scrape(base.Spider):

    def crawl(self):
        for state in html.fromstring(requests.get(base_url).text).xpath('//div[contains(@class, "sqs-gallery")]//a/@href[contains(., "-locations")]'):
            yield from self.process_request_1(state)

    def process_request_1(self, state):
        selector = base.selector(urljoin(base_url, state))
        if selector['request'].status_code == 200:
            for store in selector['tree'].xpath('//div[@class="summary-title"]/a/@href[not(contains(., "google"))]'):
                yield from self.process_request_2(store)
        else:
            logger.info("RETRYING {}...".format(state))
            yield from self.process_request_1(state)

    def process_request_2(self, store):
        store_selector = base.selector(urljoin(base_url, store))
        logger.info(store_selector['url'])
        if store_selector['request'].status_code == 200:
            hr = lambda x: '; '.join([s.strip() for s in x])
            hrs = hr(store_selector['tree'].xpath(
                '//h3[strong[contains(text(),"HOUR") or contains(text(), "HOur") or contains(text(), "Hour") or contains(text(), "hour")]]/text()'))
            if "Soon" not in hrs:
                i = base.Item(store_selector['tree'])
                i.add_value('locator_domain', store_selector['url'])
                i.add_value('hours_of_operation', hrs)
                st = store_selector['tree'].xpath('//div[@class="sqs-block-content"]/h3/a[contains(@href, "google")]//text()')
                if len(st) == 2:
                    i.add_value('street_address', st[0], lambda x: x.replace('\xa0', ' '))
                elif len(st) == 3:
                    i.add_value('street_address', ', '.join([st[0], st[1]]), lambda x: x.replace('\xa0', ' ').replace(', , ', ', '))
                st_ = st[-1].replace('\xa0', ' ')
                if ',' in st_:
                    i.add_value('city', capwords(st_[:st_.find(',')]))
                    st_ = st_.replace(st_[:st_.find(',') + 1], '').strip().replace('  ', ' ')
                else:
                    i.add_value('city', capwords(st_[:st_.find(' ')]))
                    st_ = st_.replace(st_[:st_.find(' ') + 1], '').strip().replace('  ', ' ')

                logger.info(st_)
                state_zip = st_.split(' ')
                if len(state_zip) > 1:
                    i.add_value('state', state_zip[0].upper())
                    i.add_value('zip', state_zip[1])
                i.add_xpath('phone', '//div[@class="sqs-block-content"]/h3/a[contains(@href, "tel")]/@href', base.get_first,
                            lambda x: x.replace('tel:', ' '))
                i.add_value('country_code', "US")
                i.add_xpath('location_name', '//div[@class="sqs-block-content"]/h1/text()',
                            lambda x: ' '.join(x).replace('\n', ''), lambda x: x.replace('\xa0', ' '))
                lat_long = store_selector['tree'].xpath('//div[@class="sqs-block-content"]/h3/a[contains(@href, "google")]/@href')[0]
                if lat_long:
                    if "@" in lat_long:
                        ll = lat_long.split('@')[-1].split(',')
                        i.add_value('latitude', ll[0])
                        i.add_value('longitude', ll[1])
                yield i
        else:
            logger.info("RETRYING {}...".format(store))
            yield from self.process_request_2(store)

if __name__ == '__main__':
    s = Scrape()
    s.run()
