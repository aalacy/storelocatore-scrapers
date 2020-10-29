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
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lincolnlandoil_com')


crawled = []
class Scrape(base.Spider):
    def get_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome('chromedriver', options=options)

    def crawl(self):
        base_url = "https://lincolnlandoil.com/Locations.aspx"
        driver = self.get_driver()
        driver.get(base_url)
        time.sleep(1)
        body = driver.page_source
        driver.close()
        sel = html.fromstring(body)
        for s in sel.xpath('//map[@id="locMap"]/area/@href'):
            s = urljoin(base_url, s)
            _driver = self.get_driver()
            _driver.get(s)

            loc_body = _driver.page_source
            _driver.close()
            loc_sel = html.fromstring(loc_body)
            for loc in loc_sel.xpath('//div[preceding-sibling::a[@class="mainContent"]]/div'):
                i = base.Item(loc)
                i.add_xpath('location_name', './span[2]/text()', base.get_first, lambda x: x.strip())
                i.add_value('locator_domain', base_url)
                i.add_value('page_url', s)
                data = loc.xpath('./span[last()]//text()')
                hours = {s.replace('\n','').replace('\xa0',' ').strip() for s in data}
                hours = {s for s in hours if s}
                days = {"mon", "tue", "wed", "thur", "fri", "sat", "sun", "open"}
                hours = {h for h in hours for d in days if d in h.lower()}
                i.add_value('hours_of_operation', '; '.join(hours))
                phone = [d for d in data if "main" in d.lower()]
                i.add_value('phone', phone, base.get_first, lambda x: x.lower().replace('main', '').strip())
                addr = loc.xpath('./span[2]/text()')[0]
                if addr:
                    tup = re.findall(r'(.+),?\s(.+?),\s([A-Z][A-Z])(\s(\d+))?', addr.replace('\r', '').strip())
                    if tup:
                        i.add_value('street_address', tup[0][0])
                        i.add_value('city', tup[0][1])
                        i.add_value('state', tup[0][2], lambda x: x.upper())
                        i.add_value('zip', tup[0][3], lambda x: x.strip())
                        i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                    else:
                        pass
                yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
