import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.gobigo.ca/Locations/Results"
        body = html.fromstring(requests.get(base_url).text).xpath('//div[@class="location-detailslink"]/a/@href')
        for result in body:
            selector = base.selector(result)
            i = base.Item(selector['tree'])
            i.add_value('locator_domain', result)
            i.add_xpath('location_name', '//div[@class="location-details"]/div[@class="location-title"]/text()', base.get_first)
            i.add_xpath('phone', '//div[@class="location-contact"]/text()[contains(., "Phone:")]', base.get_first, lambda x: x.replace('Phone:','').strip())
            try:
                i.add_xpath('latitude', '//div[@class="locMap"]//script/text()', base.get_first, lambda x: x.split('cLat = ')[1].split(';')[0])
                i.add_xpath('longitude', '//div[@class="locMap"]//script/text()', base.get_first, lambda x: x.split('cLon = ')[1].split(';')[0])
            except:
                pass
            i.add_xpath('street_address', '//div[@class="location-address"]/text()[1]', base.get_first, lambda x: x.replace('\n','').replace('\r','').replace('\t',''))
            czs = selector['tree'].xpath('//div[@class="location-address"]/text()[2]')[0]
            czs_re = re.findall(r'(?P<city>.+?),\s(?P<state>[A-Z][A-Z])\s(?P<zip>.+)', czs)
            i.add_value('city', czs_re[0][0], lambda x: x.replace('\t',''))
            i.add_value('state', czs_re[0][1])
            i.add_value('zip', czs_re[0][2], lambda x: x[:3]+' '+x[3:] if ' ' not in x else x)
            i.add_value('country_code', 'CA')
            i.add_xpath('hours_of_operation', '//div[@class="location-hours"]/text() | //div[@class="location-hours"]/p/text()', lambda x: '; '.join(x).replace('\n','').replace('\r','').replace('\t','').replace('  ',''))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
