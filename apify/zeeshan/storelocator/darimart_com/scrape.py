import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Darimart(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'darimart.com'
    url = 'https://www.darimart.com/locations/'

    def map_data(self, row):
        
        hxt = html.fromstring(row)

        street_address = xpath(hxt, '//strong/text()')

        city, state, zipcode = None, None, None

        region = re.findall(r'([a-zA-Z]+), ([A-Z]{2}) (\d{5})', row)
        if region and len(region[0]) == 3:
            city, state, zipcode = region[0]

        phone = None
        phone = re.findall(r'\(\d+\) \d+-\d+', row)
        phone = phone[0] if phone else phone

        geo = {}
        if zipcode:
            address = '%s, %s, %s %s' % (street_address, city, state, zipcode)
            _geo = self.get_geo(address)
            geo = _geo if _geo else geo

        return {
            'locator_domain': self.domain_name
            ,'location_name': '<MISSING>'
            ,'street_address': xpath(hxt, '//strong/text()')
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': '<MISSING>'
            ,'phone': phone
            ,'location_type': '<MISSING>'
            ,'naics_code': None
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': '<INACCESSIBLE>'
        }

    def crawl(self):
        session = requests.Session()
        request = session.get(self.url, headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Cache-Control': 'max-age=0'
            ,'Connection': 'keep-alive'
            ,'Host': 'www.darimart.com'
            ,'Referer': 'https://www.darimart.com/'
            ,'Upgrade-Insecure-Requests': '1'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        })
        if request.status_code == 200:
            rows = re.findall(r'setHTML\(\'(.+)\'\)', request.text)
            for row in rows:
                yield row


if __name__ == '__main__':
    d = Darimart()
    d.run()