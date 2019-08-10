import time

import base
from lxml import html
import requests, json
from urllib.parse import urljoin

class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.restoamir.com/english/assets/map/generatemap.php"
        r = requests.get(base_url)

        for result in html.fromstring(r.text).xpath('//marker'):
            i = base.Item(result)
            i.add_value('locator_domain', "https://www.restoamir.com/english/findarestaurant/")
            i.add_xpath('location_name', './@name', base.get_first)
            i.add_xpath('street_address', './@street', base.get_first)
            i.add_xpath('store_number', './@id', base.get_first)
            i.add_xpath('city', './@city', base.get_first)
            i.add_xpath('zip', './@zipcode', base.get_first)
            i.add_xpath('phone', './@telephone', base.get_first)
            i.add_value('country_code', 'CA')
            i.add_xpath('latitude', './@lat', base.get_first)
            i.add_xpath('longitude', './@lng', base.get_first)
            yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
