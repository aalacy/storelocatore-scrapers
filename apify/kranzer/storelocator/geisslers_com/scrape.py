import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.geisslers.com/locations/"
        body = html.fromstring(requests.get(base_url).text).xpath('//div[h4]')
        for result in body:
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_xpath('location_name', './h4/text()', base.get_first)
            i.add_xpath('phone', '//div[@class="contact"]/div[@class="tel"]/a/text()', base.get_first)
            i.add_value('latitude', '<INACCESSIBLE>')
            i.add_value('longitude', '<INACCESSIBLE>')
            i.add_xpath('phone', '//div[h4]//text()[preceding-sibling::b[1][text()="Phone:"]][1]', base.get_first, lambda x: x.strip())

            i.add_xpath('street_address', './text()[preceding-sibling::b[1][text()="Address"]][1]', base.get_first, lambda x: x.replace('\n','').replace('\r','').replace('\t','').strip())
            czs_re = re.findall(r'(?P<city>.+?),\s(?P<state>[A-Z][A-Z])\s(?P<zip>.+)', result.xpath('./text()[preceding-sibling::b[1][text()="Address"]][2]')[0])
            i.add_value('city', czs_re[0][0], lambda x: x.replace('\t', '').strip())
            i.add_value('state', czs_re[0][1])
            i.add_value('zip', czs_re[0][2])
            i.add_value('country_code', 'US')
            i.add_xpath('hours_of_operation', '//div[h4]//text()[preceding-sibling::b[1][text()="Hours:"]][1]', base.get_first, lambda x: x.replace('|', ';'))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
