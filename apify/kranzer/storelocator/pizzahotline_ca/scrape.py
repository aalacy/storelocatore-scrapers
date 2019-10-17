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
            m = re.findall(r'(1d(-.+?)!2d(.+))', text)
            if m:
                m_ = [s for s in m[0] if s]
                if m_:
                    return {"1": (m_[2][:m_[2].find('!')], m_[1][:m_[1].find('!')])}
            else:
                m = re.findall(r'(3d(.+?)!4d(-.+))|(@(.+?),(.+?),)|(sll=(.+?),(.+?)&)', text)
                if m:
                    m_ = [s for s in m[0] if s]
                    if m_:
                        return {"1": (m_[1], m_[2])}
                else:
                    return {}
        except:
            return {}

    def crawl(self):
        base_url = "https://www.pizzahotline.ca/pizzahotline/locations.htm"
        r = requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        cities = html.fromstring(r.text).xpath('//td[@class="med-gray"]/table[2]//tr/td[@valign="top"]//b/span/text()')
        body = html.fromstring(r.text).xpath('//td[@class="med-gray"]/table[2]//tr/td[@valign="top"]/a[img]')
        for result_ in body:
            alt = result_.xpath('./img/@alt')
            result = [l.replace('\n','').replace('\r', '').replace('\t', '').replace('\xa0', ' ').replace('  ', ' ').strip() for l in result_.xpath('./text()')]
            result = [l for l in result if l]+alt
            i = base.Item(result_)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            try:
                lat = result_.xpath('./@href')[0].split('latitude=')[1].split('&')[0]
                lng = result_.xpath('./@href')[0].split('longitude=')[1].split('&')[0]
                i.add_value('latitude', lat)
                i.add_value('longitude', lng)
            except:
                pass
            i.add_value('location_name', result[-1])
            i.add_value('street_address', ', '.join(result[:-2]))
            loc = result[-2]
            try:
                loc_ = re.findall(r'(.+?),\s([A-Z][A-Z])\s+(.+)', loc)
                if loc_:
                    i.add_value('city', loc_[0][0])
                    i.add_value('state', loc_[0][1])
                    i.add_value('zip', loc_[0][2])
                    i.add_value('country_code', 'CA')
                    for c in cities:
                        if i.as_dict()['city'] in c:
                            i.add_value('phone', c[c.find('('):].strip())
                            break
            except:
                pass
            yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
