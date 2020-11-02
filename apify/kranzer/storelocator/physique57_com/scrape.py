import re
from pprint import pprint
from string import capwords

import base
from sgrequests import SgRequests
import json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html, etree
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('physique57_com')


crawled = []
class Scrape(base.Spider):
    def crawl(self):
        session = SgRequests()
        
        base_url = "https://physique57.com/page-sitemap.xml"
        c = session.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}).content
        tree = etree.fromstring(c)
        for href in tree.xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            url = href.text
            if re.fullmatch(r'https://physique57\.com/studio-[^\/]+?/', url):
                city_sel = base.selector(url)
                for studio_sel in city_sel['tree'].xpath('//div[div[@class="studio-location-address"]]'):
                    loc_data = studio_sel.xpath('./div[@class="studio-location-address"]/text()')
                    loc_data = [s.strip() for s in loc_data if s.strip()]
                    i = base.Item(studio_sel)
                    if len(loc_data) == 4:
                        i.add_value('street_address', ' '.join(loc_data[:2]).replace("(at Exchange Alley)","").replace("(at Spring Street)","").strip())
                        i.add_value('phone', loc_data[-1])
                        ct = loc_data[2]
                    elif len(loc_data) == 3:
                        i.add_value('street_address', loc_data[0].replace("(at Exchange Alley)","").replace("(at Spring Street)","").strip())
                        i.add_value('phone', loc_data[-1])
                        ct = loc_data[1]
                    else:
                        i.add_value('street_address', loc_data[0])
                        ct = loc_data[1]
                    tup = re.findall(r'(.+?),\s?([A-Z]+)\s(\d+)', ct)
                    if tup:
                        i.add_value('city', tup[0][0])
                        i.add_value('state', tup[0][1], lambda x: x.upper())
                        i.add_value('zip', tup[0][2])
                        i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))

                    i.add_xpath('location_name', './div[@class="studio-location-address"]/text()[1]', base.get_first, lambda x: x.strip())
                    i.add_value('locator_domain', city_sel['url'])
                    i.add_value('page_url', city_sel['url'])
                    try:
                        lat_lng = studio_sel.xpath('./div[2]/a[contains(span, "Directions")]/@href')[0]
                        r_ = re.findall(r'@(.+?),(.+?),', lat_lng)
                        i.add_value('longitude', r_[0][1])
                        i.add_value('latitude', r_[0][0])
                    except:
                        pass

                    if (i.as_dict()['country_code'] == 'US' or i.as_dict()['country_code'] == 'CA') and "COMING SOON" not in city_sel['tree'].xpath('.//h1//text()'):
                        yield i



if __name__ == '__main__':
    s = Scrape()
    s.run()
