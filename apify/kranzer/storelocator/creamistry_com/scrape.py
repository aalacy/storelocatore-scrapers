import re
import time

from lxml import html
import base
import requests, json
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Scrape(base.Spider):

    def get_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome('chromedriver', options=options)

    def crawl(self):
        base_url = "https://creamistry.com/locations/"
        driver = self.get_driver()
        driver.get(base_url)
        time.sleep(1)
        body = driver.page_source
        driver.close()
        for result in html.fromstring(body).xpath('//div[@id="locations"]/div[contains(@class, "location")]'):
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_xpath('hours_of_operation', './/p[@class="hours"]/span', lambda x: ';'.join([s.text for s in x]))
            i.add_xpath('street_address', './/span[@itemprop="address"]/text()[1]', base.get_first)
            i.add_xpath('city', './/span[@itemprop="address"]/text()[2]', base.get_first, lambda x: x.replace('\xa0',' ').split(',')[0])
            i.add_xpath('state', './/span[@itemprop="address"]/text()[2]', base.get_first, lambda x: x.replace('\xa0',' ').split(',')[1].strip().split(' ')[0])
            i.add_xpath('zip', './/span[@itemprop="address"]/text()[2]', base.get_first, lambda x: x.replace('\xa0',' ').split(',')[1].strip().split(' ')[1])
            i.add_xpath('location_name', './/h3[@itemprop="name"]/text()', base.get_first)
            i.add_xpath('phone', './/span[@itemprop="telephone"]/text()', base.get_first)
            i.add_xpath('latitude', './@lat', base.get_first)
            i.add_xpath('longitude', './@lng', base.get_first)
            i.add_value('country_code', 'US')
            i.add_xpath('store_number', './@id', base.get_first)
            yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
