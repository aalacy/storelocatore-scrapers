import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
class Scrape(base.Spider):
    crawled = set()
    def crawl(self):
        base_url = "https://behandpicked.com/store-locations"
        body = set(html.fromstring(requests.get(base_url).text).xpath('//div[contains(@class, "page-content")]//a/@href[not(contains(., "mailto"))]'))
        for result in body:
            res_sel = base.selector(result)
            if res_sel['request'].status_code == 200:
                i = base.Item(res_sel['tree'])
                i.add_value('locator_domain', base_url)
                i.add_value('page_url', res_sel['url'])
                i.add_xpath('location_name', '//title/text()', base.get_first)
                i.add_xpath('phone', '//h4//text()[contains(., "Phone")]', base.get_first,
                            lambda x: x.replace('Phone', '').strip().replace('#', '').replace(':','').strip())
                if i.as_dict()['phone'] == "<MISSING>":
                    i.add_xpath('phone', '//h4[contains(text(), "Phone")]//a/text()', base.get_first)
                # i.add_value('location_type', json_resp['@type'])
                i.add_xpath('latitude', '//div[@class="shg-map-container"]/@data-latitude', base.get_first)
                i.add_xpath('longitude', '//div[@class="shg-map-container"]/@data-longitude', base.get_first)
                loc = res_sel['tree'].xpath('//div[@class="shg-map-container"]/@data-description')[0]
                tup = re.findall(r'(.+),\s(.+?),?\s([A-Z][A-Z])\s(.+)', loc.replace('\r', '').strip())
                if tup:
                    i.add_value('street_address', tup[0][0])
                    i.add_value('city', tup[0][1])
                    i.add_value('state', tup[0][2], lambda x: x.upper())
                    i.add_value('zip', tup[0][3])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                if i.as_dict()['location_name'] not in self.crawled:
                    self.crawled.add(i.as_dict()['location_name'])
                    yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
