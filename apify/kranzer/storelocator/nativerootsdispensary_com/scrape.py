import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.nativerootsdispensary.com/location"
        body = html.fromstring(requests.get(base_url).text).xpath('//div[@class="content-item"]/a/@href')
        for result in body:
            url = urljoin(base_url, result)
            selector = base.selector(url)
            i = base.Item(selector['tree'])
            i.add_value('locator_domain', url)
            i.add_xpath('location_name', '//div[@class="block-title"]/h1//div[contains(@class, "field-item")]/text()', lambda x: [s.replace('\n','').strip() for s in x if s.replace('\n','').strip()], base.get_first)
            i.add_xpath('phone', '//div[@class="contact"]/div[@class="tel"]/a/text()', base.get_first)
            try:
                i.add_xpath('latitude', '//script/text()[contains(., "lon")]', base.get_first, lambda x: x.split('\"lat\":\"')[1].split('"')[0])
                i.add_xpath('longitude', '//script/text()[contains(., "lon")]', base.get_first, lambda x: x.split('\"lon\":\"')[1].split('"')[0])
            except:
                pass
            i.add_xpath('street_address', '//div[@itemprop="address"]//div[@class="street-block"]/div[@itemprop="streetAddress"]/text()', base.get_first, lambda x: x.replace('\n','').replace('\r','').replace('\t',''))
            i.add_xpath('city', '//div[@itemprop="address"]//div[contains(@class,"addressfield-container-inline")]/span[@class="locality"]/text()', base.get_first)
            i.add_xpath('state', '//div[@itemprop="address"]//div[contains(@class,"addressfield-container-inline")]/span[@class="state"]/text()', base.get_first)
            i.add_xpath('zip', '//div[@itemprop="address"]//div[contains(@class,"addressfield-container-inline")]/span[@class="postal-code"]/text()', base.get_first)
            i.add_xpath('location_type', '//div[@class="contact"]/p/text()', lambda x: [s.strip() for s in x if s.strip()])
            i.add_value('country_code', 'US')
            i.add_xpath('hours_of_operation', '//div[@class="contact"]/div[@class="info"]//div[@class="field-items"]/div/text()', lambda x: '; '.join(x).replace('\n','').replace('\r','').replace('\t','').replace('  ',''))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
