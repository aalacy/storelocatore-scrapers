import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('myplacehotels_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        js = html.fromstring(requests.get('https://www.myplacehotels.com/locations').text).xpath(
            '//script[contains(text(), "propertiesList")]/text()')[0].replace('var propertiesList = ', '').strip()
        for _, sel in json.loads(js[:-1]).items():
            if not sel.get('underConstruction'):
                i = base.Item(sel)
                i.add_value('location_name', sel['name'])
                i.add_value('locator_domain', 'https://www.myplacehotels.com/locations')
                i.add_value('page_url', urljoin('https://www.myplacehotels.com/locations', sel['slug']))
                i.add_value('phone', sel['phone'])
                i.add_value('latitude', sel['lat'])
                i.add_value('longitude', sel['lng'])
                i.add_value('street_address', sel['street_address'].replace(sel['city_name'], '').replace(sel['state_abbreviation'], '').strip(), lambda x: x[:-1] if x[-1] == ',' else x)
                i.add_value('city', sel['city_name'])
                i.add_value('state', sel['state_abbreviation'])
                i.add_value('zip', sel['zip'])
                i.add_value('country_code', sel['country_abbreviation'])
                i.add_value('store_number', sel['id'])
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
