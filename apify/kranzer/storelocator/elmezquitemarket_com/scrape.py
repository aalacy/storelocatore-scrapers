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
        base_url = "https://www.elmezquitemarket.com/locations.aspx"
        body = html.fromstring(requests.get(base_url).text).xpath('//div[contains(@id, "Content")][h3]')[0].xpath('./*')
        results = [html.fromstring(res) for res in b''.join([html.tostring(b) for b in body]).decode('utf8').split('<hr>')]
        for result in results:
            centroid_map = self.get_centroid_map(result.xpath('./p/iframe/@src')[0])
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_xpath('location_name', './h3/text()', base.get_first)
            i.add_xpath('street_address', './p[1]/text()', base.get_first)
            tup = re.findall(r'(.+?),\s?(.+?)\s(\d+)', result.xpath('./p[1]/text()[2]')[0])
            if tup:
                i.add_value('city', tup[0][0])
                i.add_value('state', tup[0][1])
                i.add_value('zip', tup[0][2])
                i.add_value('country_code', 'US')
            i.add_xpath('phone', './p[1]/text()[contains(., "Phone:")]', base.get_first, lambda x: x.replace('Phone:','').strip())
            i.add_xpath('hours_of_operation', './p', lambda x: x[1:-1], lambda x: [s.text for s in x], lambda x: [s.replace('\xa0',' ').strip() for s in x], lambda x: '; '.join([s for s in x if s]))
            i.add_value('longitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[0])
            i.add_value('latitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[1])
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
