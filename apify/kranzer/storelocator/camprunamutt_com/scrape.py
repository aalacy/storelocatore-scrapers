import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.camprunamutt.com/locations.php"
        # json_body = json.loads(html.fromstring(requests.get(base_url).text).xpath('//script[@type="application/json"]/text()')[0])
        body = html.fromstring(requests.get(base_url).text).xpath('//div[@class="location"]/div/a/@href')
        for result in body:
            selector = base.selector(urljoin(base_url, result))
            i = base.Item(selector['tree'])
            i.add_value('locator_domain', selector['url'])
            i.add_xpath('location_name', '//h4[preceding-sibling::h2[1][contains(text(), "Camp")]][1]/text()', base.get_first)
            i.add_value('latitude', '<INACCESSIBLE>')
            i.add_value('longitude', '<INACCESSIBLE>')
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
