import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def get_centroid_map(self, text):
        centroid_map = {}
        try:
            m = re.match(r'^.*!2d(-[\d\.]+)!3d([\d\.]+)!.*$', text)
            if m:
                centroid_map['1'] = (m.group(1), m.group(2))
            return centroid_map
        except:
            return {}

    def crawl(self):
        base_url = "https://www.sunstonefit.com/studios"
        body = html.fromstring(requests.get(base_url).text).xpath('//a[@itemprop="url"]/@href')
        for result in body:
            if len(result.replace('/','')) > 0:
                result = urljoin(base_url, result)
                sel = base.selector(result)
                centroid_map = self.get_centroid_map(sel['tree'].xpath('.//div[@class="map-responsive"]/iframe/@src')[0])
                i = base.Item(sel['tree'])
                i.add_value('locator_domain', base_url)
                i.add_value('page_url', sel['url'])
                i.add_xpath('location_name', './/div[@class="main"]//h3/span[@itemprop="name"]/text()', base.get_first)
                i.add_xpath('street_address', './/div[@class="main"]//span[@itemprop="address"]/span[@itemprop="streetAddress"]/text()', base.get_first)
                i.add_xpath('city', '//div[@class="main"]//span[@itemprop="address"]/span[@itemprop="addressLocality"]/text()', base.get_first)
                i.add_xpath('state', '//div[@class="main"]//span[@itemprop="address"]/span[@itemprop="addressRegion"]/text()', base.get_first)
                i.add_xpath('zip', '//div[@class="main"]//span[@itemprop="address"]/span[@itemprop="postalCode"]/text()', base.get_first)
                i.add_xpath('phone', '//div[@class="main"]//span[@itemprop="address"]/span[@itemprop="telephone"]/text()', base.get_first)
                i.add_value('longitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[0])
                i.add_value('latitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[1])
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                if i.as_dict()['street_address'] != "<MISSING>":
                    yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
