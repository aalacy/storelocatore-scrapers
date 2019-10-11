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
        base_url = "https://snoozeeatery.com/locations"
        # json_body = json.loads(html.fromstring(requests.get(base_url).text).xpath('//script[@type="application/json"]/text()')[0])
        body = html.fromstring(requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}).text).xpath('//li[a[contains(text(), "locations")]]/ul/li//div/ul[not(li="Coming Soon")]/li/a/@href')
        for result in body:
            selector = base.selector(urljoin(base_url, result), headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            i = base.Item(selector['tree'])
            centroid_map = self.get_centroid_map(selector['tree'].xpath('//div[@id="map"]/iframe/@src')[0])
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', selector['url'])
            i.add_xpath('location_name', './/div[@class="locationInfoText"]/div[@class="block"][1]/h2/text()', base.get_first)
            i.add_xpath('phone', './/div[@class="locationInfoText"]/div[@class="block"][4]/text()', base.get_first)
            loc = selector['tree'].xpath('.//div[@class="locationInfoText"]/div[@class="block"][2]/text()[last()]')[0]
            if loc:
                tup = re.findall(r'(.+?),?\s([A-Z]+|California),?\s(\d+)', loc.replace('\r','').strip())
                if tup:
                    i.add_value('city', tup[0][0])
                    i.add_value('state', tup[0][1])
                    i.add_value('zip', tup[0][2])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                    i.add_xpath('street_address', '//div[@class="block"][2]/text()[position() < last()]', lambda x: ', '.join(x).replace('\r','').replace('\n', '').strip())
                else:
                    i.add_xpath('street_address', '//div[@class="block"][2]/text()', base.get_first)
            i.add_value('longitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[0])
            i.add_value('latitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[1])
            i.add_xpath('hours_of_operation', './/div[@class="locationInfoText"]/div[@class="block"][3]/text()', lambda x: ' '.join(x).replace('\r','').replace('\n', ''))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
