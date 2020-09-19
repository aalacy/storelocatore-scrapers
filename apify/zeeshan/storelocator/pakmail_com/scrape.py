import re 
import base
import random
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class PakMail(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'pakmail.com'
    url = 'https://www.pakmail.com/store-locator'

    def map_data(self, row):

        street_address = xpath(row, './/div[@class="layout-3col__col-2"]/text()[following-sibling::br]').strip()

        zipcode = xpath(row, './/div[@class="layout-3col__col-2"]/text()[preceding-sibling::br]').strip()
        zipcode = re.findall(r'\d{5}', zipcode)
        zipcode = zipcode[0] if zipcode else ''
        
        city_state = xpath(row, './/a[1]/text()')
        city, state = city_state.split(',')

        store_number = xpath(row, './/a[1]/@href')[1:]

        phone = re.findall(r'\d{10}', etree.tostring(row))
        phone = phone[0] if phone else ''

        address = '%s, %s, %s %s' % (street_address, city, state, zipcode)
        geo = self.get_geo(address) or {}

        return {
            'locator_domain': self.domain_name
            ,'location_name': ''
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': store_number
            ,'phone': phone
            ,'location_type': None
            ,'naics_code': None
            ,'latitude': geo.get('lat', '<MISSING>')
            ,'longitude': geo.get('lng', '<MISSING>')
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'authority': 'www.pakmail.com'
            ,'method': 'GET'
            ,'path': '/store-locator'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'cache-control': 'max-age=0'
            ,'if-modified-since': 'Sat, 20 Jul 2019 17:07:28 GMT'
            ,'if-none-match': 'W/"1563642448-0"'
            ,'referer': 'https://www.pakmail.com/'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        })
        request = session.get(self.url)
        if request.status_code == 200:
            hxt = html.fromstring(request.text)
            rows = hxt.xpath('//div[@class="layout-3col blockish address-list"]')
            for row in rows:
                yield row


if __name__ == '__main__':
    pm = PakMail()
    pm.run()
