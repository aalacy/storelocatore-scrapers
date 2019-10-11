import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import etree
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        for sel in requests.get('https://www.mydriversedge.com/wp-admin/admin-ajax.php?action=store_search&lat=32.776664&lng=-96.796988&max_results=25&search_radius=50&autoload=1', headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}).json():
            i = base.Item(sel)
            i.add_value('location_name', sel['store'])
            i.add_value('locator_domain', 'https://www.mydriversedge.com/locations/')
            i.add_value('page_url', sel['permalink'])
            i.add_value('phone', sel['phone'])
            i.add_value('latitude', sel['lat'])
            i.add_value('longitude', sel['lng'])
            i.add_value('street_address', sel['address'])
            i.add_value('city', sel['city'])
            i.add_value('state', sel['state'])
            i.add_value('zip', sel['zip'])
            i.add_value('country_code', sel['country'])
            i.add_value('store_number', sel['id'])
            selector = base.selector(sel['permalink'], headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            i.add_value('hours_of_operation', '; '.join([''.join(s.xpath('./td//text()')).replace('\xa0',' ') for s in selector['tree'].xpath('//table[contains(@class, "hours-list")]//tr')]))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
