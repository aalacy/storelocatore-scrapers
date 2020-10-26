import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('scriveneroil_com')


crawled = []
class Scrape(base.Spider):
    def get_centroid_map(self, text):
        centroid_map = {}
        try:
            m = re.match(r'^.*!2d(-[\d\.]+)!3d([\d\.]+)!.*$', text)
            if m:
                centroid_map['1'] = (m.group(1), m.group(2))
            return centroid_map
        except:
            return {}

    def crawl(self):
        base_url = "http://scriveneroil.com/locations/"
        sel = base.selector(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for href in sel['tree'].xpath('//tr[count(td)=2]'):
            i = base.Item(href)
            centroid_map = self.get_centroid_map(href.xpath('./td[2]/iframe/@src')[0])
            i.add_xpath('location_name', './td[1]/text()[1]', base.get_first, lambda x: x.strip())
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_xpath('phone', '(./td[1]//text())[last()]', base.get_first, lambda x: x.replace('\n', ''))
            index = None
            loc = [l.replace('\n','') for l in href.xpath('./td[1]//text()')]
            loc = [l for l in loc if l]
            for l in loc:
                tup = re.findall(r'(.+?),\s?([A-z][A-z]|Missouri)\s(\d+)', l)
                if tup:
                    i.add_value('city', tup[0][0])
                    i.add_value('state', tup[0][1], lambda x: x.upper(), lambda x: "MO" if x == "MISSOURI" else x)
                    i.add_value('zip', tup[0][2])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                    index = loc.index(l)
                    break
                else:
                    tup = re.findall(r'(.+?),\s?([A-z][A-z]|Missouri)', l)
                    if tup:
                        i.add_value('city', tup[0][0])
                        i.add_value('state', tup[0][1], lambda x: x.upper(), lambda x: "MO" if x == "MISSOURI" else x)
                        i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                        index = loc.index(l)
                        break

            if index:
                i.add_value('street_address', loc[index-1])

            i.add_value('longitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[0])
            i.add_value('latitude', centroid_map.get('1', ("<MISSING>", "<MISSING>"))[1])
            yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
