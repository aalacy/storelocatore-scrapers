import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pizzapro_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://pizzapro.com/store-locator"
        locations = requests.get('https://pizzapro.com/src/scripts/load-locations-csv.php').json()
        for result in locations[1:]:
            if result[0] is not None:
                if ''.join(result) != "":
                    i = base.Item(result)
                    i.add_value('locator_domain', base_url)
                    i.add_value('page_url', base_url)
                    i.add_value('city', result[0])
                    i.add_value('state', result[1])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                    i.add_value('street_address', result[2])
                    i.add_value('zip', result[3])
                    i.add_value('phone', result[4])
                    yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
