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
            key = None
            for line in text.splitlines():
                if key:
                    m = re.match(r'^.*!2d(-[\d\.]+)!3d([\d\.]+)!.*$', line)
                    if m:
                        centroid_map[key] = (m.group(1), m.group(2))
                    key = None
                m = re.match(r'^.*case "([a-z]+)":.*$', line)
                if m:
                    key = m.groups(1)[0]
            return centroid_map
        except:
            return {}
                

    def crawl(self):
        base_url = "https://www.camprunamutt.com/locations.php"
        centroid_map = self.get_centroid_map(requests.get(base_url).text)
        body = html.fromstring(requests.get(base_url).text).xpath('//div[@class="location"]/div/a/@href')
        for result in body:
            selector = base.selector(urljoin(base_url, result))
            i = base.Item(selector['tree'])
            i.add_value('locator_domain', selector['url'])
            i.add_xpath('location_name', '//h4[preceding-sibling::h2[1][contains(text(), "Camp")]][1]/text()', base.get_first)
            i.add_value('latitude', centroid_map.get(result[:-1], ("<MISSING>", "<MISSING>"))[0])
            i.add_value('longitude', centroid_map.get(result[:-1], ("<MISSING>", "<MISSING>"))[1])
            czs = selector['tree'].xpath('//p[@class="campAddress"]/text()[2]')[0]
            czs_re = re.findall(r'(?P<city>.+?),\s(?P<state>[A-Z][A-Z])\s(?P<zip>.+)', czs)
            i.add_value('city', czs_re[0][0], lambda x: x.replace('\t', ''), lambda x: x.replace('\n', '').strip())
            i.add_value('state', czs_re[0][1])
            i.add_value('zip', czs_re[0][2])
            i.add_xpath('street_address', '//p[@class="campAddress"]/text()[1]', base.get_first, lambda x: x.replace('\n', '').strip())
            i.add_xpath('phone', '//p[@class="campAddress"]/text()[contains(., "phone: ")]', base.get_first, lambda x: x.replace('phone: ', ''), lambda x: x.replace('\n', '').strip())
            i.add_value('country_code', 'US')
            i.add_xpath('hours_of_operation', '//p[preceding-sibling::h4[1][contains(text(), "Business")]]/text()', lambda x: '; '.join([s.strip() for s in x]))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
