import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import etree
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.picknsave.com/storelocator-sitemap.xml"
        for sel in etree.fromstring(requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}).content).xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            url = sel.text
            if "details" in url:
                sel = base.selector(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
                i = base.Item(sel['tree'])
                i.add_xpath('location_name', '//h1[@class="StoreDetails-header"]/text()', lambda x: ' '.join(x))
                i.add_value('locator_domain', 'https://www.picknsave.com/storelocator')
                i.add_value('page_url', sel['url'])
                js = sel['tree'].xpath('//div[@class="StoreDetails"]/script/text()')[0]
                info = json.loads(js.replace('&quot;', '"'))
                i.add_value('hours_of_operation', '; '.join(info['openingHours']))
                i.add_value('phone', info['telephone'])
                i.add_value('latitude', info['geo']['latitude'])
                i.add_value('longitude', info['geo']['longitude'])
                i.add_value('street_address', info['address']['streetAddress'])
                i.add_value('city', info['address']['addressLocality'])
                i.add_value('state', info['address']['addressRegion'])
                i.add_value('zip', info['address']['postalCode'])
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                i.add_value('store_number', url.split('/')[-1])
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
