import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://casaraul.com/pages/about-us"
        # json_body = json.loads(html.fromstring(requests.get(base_url).text).xpath('//script[@type="application/json"]/text()')[0])
        body = html.fromstring(requests.get(base_url).text).xpath('//table/tbody/tr/td')
        for result in body:
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_xpath('location_name', './p[1]/text()', base.get_first, lambda x: x.replace('\xa0', ' ').strip())
            i.add_xpath('phone', './p[3]/text()', base.get_first)
            czs = result.xpath('./p[2]/text()[2]')[0]
            czs_re = re.findall(r'(?P<city>.+?),\s(?P<state>.+?)\s(?P<zip>.+)', czs)
            i.add_value('city', czs_re[0][0], lambda x: x.replace('\t', ''), lambda x: x.replace('\n', '').strip())
            i.add_value('state', czs_re[0][1])
            i.add_value('zip', czs_re[0][2])
            i.add_xpath('street_address', './p[2]/text()[1]', base.get_first, lambda x: x.replace('\n', '').strip())
            i.add_value('country_code', 'US')
            print(i)
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
