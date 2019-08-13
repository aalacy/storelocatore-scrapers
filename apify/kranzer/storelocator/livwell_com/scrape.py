import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.livwell.com/marijuana-dispensary-locations/"
        # json_body = json.loads(html.fromstring(requests.get(base_url).text).xpath('//script[@type="application/json"]/text()')[0])
        body = html.fromstring(requests.get(base_url).text).xpath('//li[contains(@class, "margin-maps")]')
        for result in body:
            i = base.Item(result)
            i.add_xpath('locator_domain', './p[1]/a/@href', base.get_first)
            i.add_xpath('location_name', './p[1]/a/text()', base.get_first)
            i.add_xpath('phone', './p[strong[contains(text(), "T.")]]/text()', base.get_first)
            i.add_xpath('location_type', './p[2]/text()')
            try:
                i.add_xpath('latitude', './div[1]/a/@href', lambda x: x[0].split('@')[1].split(',')[0])
                i.add_xpath('longitude', './div[1]/a/@href', lambda x: x[0].split('@')[1].split(',')[1])
            except:
                pass
            i.add_xpath('city', './p[3]/text()[2]', base.get_first, lambda x: x.split(',')[0].strip())
            i.add_xpath('street_address', './p[3]/text()[1]', base.get_first)
            i.add_xpath('state', './p[3]/text()[2]',base.get_first, lambda x: x.split(',')[1].strip().split(' ')[0])
            i.add_xpath('zip', './p[3]/text()[2]', base.get_first, lambda x: x.split(',')[1].strip().split(' ')[1])
            i.add_value('country_code', 'US')
            i.add_xpath('hours_of_operation', './p[strong[contains(text(), "Hours")]]/text()', base.get_first)
            print(i)
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
