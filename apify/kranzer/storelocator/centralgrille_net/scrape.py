import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "http://centralgrille.net/"
        # json_body = json.loads(html.fromstring(requests.get(base_url).text).xpath('//script[@type="application/json"]/text()')[0])
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        }
        body = html.fromstring(requests.get(base_url, headers=headers).text).xpath('//div[@class="row"]/div/a/@href')
        for result in body:
            selector = base.selector(urljoin(base_url, result+'/location/'), headers=headers)
            i = base.Item(selector['tree'])
            i.add_value('locator_domain', selector['url'])
            czs = selector['tree'].xpath('//div[@id="cont-loc"]/*[preceding-sibling::h1[1][contains(text(), "Location")]][2]/text()')[0]
            czs_re = re.findall(r'(?P<city>.+?),\s(?P<state>[A-Z][A-Z])\s(?P<zip>.+)', czs)
            i.add_value('city', czs_re[0][0], lambda x: x.replace('\t', ''), lambda x: x.replace('\n', '').strip())
            i.add_value('state', czs_re[0][1])
            i.add_value('zip', czs_re[0][2])
            i.add_xpath('street_address', '//div[@id="cont-loc"]/*[preceding-sibling::h1[1][contains(text(), "Location")]][1]/text()', base.get_first, lambda x: x.replace('\n', '').strip())
            i.add_xpath('phone', '//div[@id="cont-loc"]/span[small="Phone:"]/text()', base.get_first)
            i.add_value('country_code', 'US')
            i.add_xpath('hours_of_operation', '//span[preceding-sibling::h1[1][contains(text(), "HOURS")]]', lambda x: '; '.join([''.join([s_.strip() for s_ in s.xpath('.//text()')]) for s in x]))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
