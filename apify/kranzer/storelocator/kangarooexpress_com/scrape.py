import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://kangarooexpress.com/store-locator"
        body = requests.get(base_url).text
        sel = html.fromstring(body).xpath('//script/text()[contains(., "locations = ")]')[0].replace('\n','')
        js_st = "[{}]".format(re.findall(r'.+?locations = \[(.+?)\];', sel)[0].strip())
        json_body = json.loads(js_st.replace('"', '\\"').replace('\'', '"').replace('  ', '').replace(',}','}').replace(',]',']'))
        for result in json_body:
            i = base.Item(result)
            status = result.get('status', '')
            if status == "Open":
                i.add_value('store_number', result.get('store_number', ''))
                i.add_value('latitude', result.get('lat', ''))
                i.add_value('longitude', result.get('lon', ''))
                html_ = html.fromstring(result.get('html', ''))
                href = html_.xpath('//a[contains(text(), "Location Details")]/@href')
                if href:
                    url = urljoin(base_url, href[0])
                    yield self.get_details(url, i)

    def get_details(self, url, item):
        selector = base.selector(url)
        item.add_value('hours_of_operation', selector['tree'].xpath('//div[preceding-sibling::h4[1][contains(text(), "Hours")]]/div/div/text()'), lambda x: [s_.strip() for s_ in x if s_],lambda x: '; '.join([' '.join(x) for x in zip(x[0::2], x[1::2])]).replace('\n', '').strip(), lambda x: x[2:] if x.startswith('; ') else x)
        item.add_value('phone', selector['tree'].xpath('//h4[contains(@class, "phone-number")]/text()'), base.get_first)
        item.add_value('street_address', selector['tree'].xpath('//h1/text()[1]'), base.get_first)
        csz = selector['tree'].xpath('//h1/text()[2]')
        if csz:
            csz_ = csz[0].split(', ')
            item.add_value('city', csz_[0])
            item.add_value('state', csz_[1])
            item.add_value('zip', csz_[2])
        item.add_value('country_code', base.get_country_by_code(item.as_dict()['state']))
        return item

if __name__ == '__main__':
    s = Scrape()
    s.run()
