import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.georgiosofp.com/locations1"
        body = html.fromstring(requests.get(base_url).text).xpath('//div[contains(@class, "row")][contains(@class, "sqs-row")]/div[contains(@class, "col")]/div[contains(@class, "sqs-block")][contains(@class, "html-block")][div/h2]')
        for result in body:
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_xpath('location_name', './div/h2/text()', base.get_first, capwords)
            i.add_xpath('phone', '//div[@class="contact"]/div[@class="tel"]/a/text()', base.get_first)
            try:
                i.add_xpath('latitude', './div/p/a[1]/@href', base.get_first, lambda x: x.split('@')[1].split(',')[0])
                i.add_xpath('longitude', './div/p/a[1]/@href', base.get_first, lambda x: x.split('@')[1].split(',')[1])
            except:
                pass
            i.add_xpath('phone', './div/p/text()[2]', base.get_first, lambda x: x.strip())
            czs_re = re.findall(r'(?P<street>.+?),?\s(?P<city>{}.+?),\s(?P<state>[A-Z][A-Z])\s(?P<zip>.+)'.format(capwords(i.as_dict()['location_name'][:3])), result.xpath('./div/p/text()[1]')[0])
            i.add_value('street_address', czs_re[0][0], lambda x: x.replace('\t', '').strip())
            i.add_value('city', czs_re[0][1], lambda x: x.replace('\t', '').strip())
            i.add_value('state', czs_re[0][2])
            i.add_value('zip', czs_re[0][3])
            i.add_value('country_code', 'US')
            i.add_xpath('hours_of_operation', '//div[h4]//text()[preceding-sibling::b[1][text()="Hours:"]][1]', base.get_first, lambda x: x.replace('|', ';'))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
