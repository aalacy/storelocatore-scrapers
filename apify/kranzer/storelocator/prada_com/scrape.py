import re
import time
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from w3lib.html import remove_tags
from lxml import html
crawled = []
class Scrape(base.Spider):
    def crawl(self):
        base_url = "https://www.prada.com/us/en/store-locator.html"
        url = "https://www.prada.com/us/en/store-locator.glb.getStores.json"
        js = requests.get(url).json()
        for _, res in js.items():
            results = []
            if isinstance(res, dict):
                results.append(res)
            elif isinstance(res, list):
                results += res
            for result in results:
                i = base.Item(result)
                i.add_value('locator_domain', base_url)
                i.add_value('page_url', base_url)
                i.add_value('location_name', result.get('Description', [])[0].get('displayStoreName'))
                i.add_value('street_address', result.get('addressLine', [])[0])
                i.add_value('city', result.get('city', ''))
                i.add_value('state', result.get('stateOrProvinceName', ''))
                i.add_value('zip', result.get('postalCode', ''), lambda x: x.strip())
                i.add_value('phone', result.get('telephone1', ''), lambda x: x.strip())
                i.add_value('country_code', result.get('country', ''))
                i.add_value('latitude', result.get('latitude', ''))
                i.add_value('longitude', result.get('longitude', ''))
                i.add_value('store_number', result.get('uniqueID',''))
                i.add_value('hours_of_operation', ''.join([f"{k}: {v}" for k, v in result.get('workingSchedule', {}).items()]))
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
