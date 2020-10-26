import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import etree
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('staples_ca')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://stores.staples.ca/"
        r = requests.get('https://stores.staples.ca/api/5d3b0e02763b7ca0181ab030/locations-details')
        for info in r.json()['features']:
            i = base.Item(info)
            i.add_value('location_name', info['properties']['name'])
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', info['properties']['website'])
            hours = []
            for k, v in info['properties']['hoursOfOperation'].items():
                if v:
                    hours.append('{} {}-{}'.format(k, v[0][0], v[0][1]))
                else:
                    hours.append('{} {}'.format(k, "Closed."))
            if hours:
                i.add_value('hours_of_operation', '; '.join(hours))
            i.add_value('phone', info['properties']['phoneNumber'])
            i.add_value('latitude', info['geometry']['coordinates'][1])
            i.add_value('longitude', info['geometry']['coordinates'][0])
            i.add_value('street_address', ' '.join([s for s in [info['properties']['addressLine1'], info['properties']['addressLine2']] if s]))
            i.add_value('city', info['properties']['city'])
            i.add_value('state', info['properties']['province'])
            i.add_value('zip', info['properties']['postalCode'])
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_value('store_number', info['properties']['branch'], lambda x: x.replace('CA-',''))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
