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
        base_url = "http://henny-penny.com/locations/"
        body = html.fromstring(requests.get(base_url).text).xpath('//div[@class="container"][preceding-sibling::h1[1][contains(text(), "Locations")]]/div[@class="row"][count(div)=1]')
        for result in body:
            centroid_map = self.get_centroid_map(result.xpath('.//div[@class="google-maps"]/iframe/@src')[0])
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_xpath('location_name', './div/h3/text()', base.get_first)
            data = [s.strip() for s in result.xpath('./div/div[1]//text()') if s.strip()]
            data[1:] = data[1].split('\n')
            data = [d.replace('\r', '').replace('\t', '') for d in data]
            i.add_value('store_number', data[0], lambda x: x.replace('Store #', ''))
            i.add_value('zip', data, lambda x: [s for s in x if i.as_dict()['location_name'] in s], base.get_first, lambda x: x.replace(i.as_dict()['location_name'], '').strip())
            i.add_value('street_address', data[1])
            i.add_value('phone', data[-2])
            i.add_value('hours_of_operation', data[-1])
            i.add_value('city', i.as_dict()['location_name'], lambda x: x.split(', ')[0])
            i.add_value('state', i.as_dict()['location_name'], lambda x: x.split(', ')[1])
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_value('longitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[0])
            i.add_value('latitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[1])
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
