import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "http://glory-supermarket.com/store-locations"
        r = requests.get(base_url, headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"})
        body = html.fromstring(r.text).xpath('//div[@class="item-list"]/ul/li/a/@href')
        for result in body:
            url = urljoin(base_url, result)
            selector = base.selector(url, headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"})
            i = base.Item(selector['tree'])
            i.add_value('locator_domain', url)
            i.add_xpath('location_name', '//h1[@id="page-title"]/text()', lambda x: [s.replace('\n','').strip() for s in x if s.replace('\n','').strip()], base.get_first)
            i.add_xpath('phone', '//div[contains(@class, "field-name-field-store-phone")]/a/text()', lambda x: [s.replace('\n','').strip() for s in x if s.replace('\n','').strip()], base.get_first)
            try:
                i.add_xpath('latitude', '//script/text()[contains(., "lon")]', base.get_first, lambda x: x.split('\"lat\":')[1].split('"')[0])
                i.add_xpath('longitude', '//script/text()[contains(., "lon")]', base.get_first, lambda x: x.split('\"lon\":')[1].split('"')[0].split('}')[0])
            except:
                pass
            i.add_xpath('street_address', '//div[@class="street-block"]/div/text()', base.get_first, lambda x: x.replace('\n','').replace('\r','').replace('\t',''))
            i.add_xpath('city', '//div[contains(@class,"addressfield-container-inline")]/span[@class="locality"]/text()', base.get_first)
            i.add_xpath('state', '//div[contains(@class,"addressfield-container-inline")]/span[@class="state"]/text()', base.get_first)
            i.add_xpath('zip', '//div[contains(@class,"addressfield-container-inline")]/span[@class="postal-code"]/text()', base.get_first)
            i.add_value('country_code', 'US')
            i.add_xpath('hours_of_operation', '//div[contains(@class, "field-name-field-store-hours")]/p/text()', lambda x: '; '.join(x).replace('\n','').replace('\r','').replace('\t','').replace('  ',''))
            print(i)
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
