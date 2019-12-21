import re

import base
from urllib.parse import urljoin

class Scrape(base.Spider):
    def get_centroid_map(self, text):
        centroid_map = {}
        try:
            m = re.findall(r'@(.+?),(.+?),', text)
            if m:
                centroid_map['1'] = (m[0][0], m[0][1])
            return centroid_map
        except:
            return {}
    def crawl(self):
        base_url = "https://www.finks.com/pages/store-directory"
        locations = base.selector(base_url)
        for location_url in locations['tree'].xpath('//a[@class="go-link"]/@href'):
            location = base.selector(urljoin(base_url, location_url))
            i = base.Item(location['tree'])
            centroid_map = self.get_centroid_map(
                location['tree'].xpath('//div[contains(@class, "location-header__text")]//a[contains(@href, "/maps/")]/@href')[0])
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', location['url'])
            i.add_xpath('location_name', '//h1[@class="page-title"]/text()', base.get_first)
            texts = location['tree'].xpath('//div[contains(@class, "location-header__text")]//div/address//text()')

            i.add_value('street_address', ', '.join(texts[:-1]), lambda x: x.replace('\n', '').strip())
            tup = re.findall(r'(.+?),\s?([A-Z]+)\s(\d+)', texts[-1])
            if tup:
                i.add_value('city', tup[0][0])
                i.add_value('state', tup[0][1], lambda x: x.upper())
                i.add_value('zip', tup[0][2])
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_xpath('phone', '//a[contains(@class, "location-contact__method")][contains(@href, "tel:")]/span/text()', base.get_first)
            i.add_value('longitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[1])
            i.add_value('latitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[0])
            i.add_xpath('hours_of_operation', './/div[preceding-sibling::h3[1][contains(text(), "Hours")]]//text()', lambda x: '; '.join([s for s in x if s.strip()]).replace('\n','').strip())
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
