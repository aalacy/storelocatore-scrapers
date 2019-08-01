import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Sandellasusa(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'sandellasusa.com'
    url = 'https://sandellasusa.com/locations'

    def map_data(self, row):

        text = etree.tostring(row)

        name = xpath(row, './/span//text()').strip()
        
        street_address = None
        street_address = re.findall(r'([0-9]+) ([A-Z0-9a-z]+) ([A-Z0-9a-z]+)', text)
        if street_address:
            street_address = ' '.join(street_address[0])

        city, state, zipcode = None, None, None
        region = re.findall(r'([A-Za-z]+)(,|) ([A-Z]+) ([0-9]+)', text)
        if region:
            city, _, state, zipcode = region[0]

        phone = re.findall(r'\d+-\d+-\d+', text)
        phone = phone[0] if phone else '<MISSING>'

        address = '%s, %s' % (street_address, region)
        geo = {} # self.get_geo(address)

        return {
            'locator_domain': self.domain_name
            ,'location_name': name
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': '<MISSING>'
            ,'phone': phone
            ,'location_type': '<MISSING>'
            ,'naics_code': '<MISSING>'
            ,'latitude': geo.get('lat', '<MISSING>')
            ,'longitude': geo.get('lng', '<MISSING>')
            ,'hours_of_operation': '<MISSING>'
        }


    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'authority': 'sandellasusa.com'
            ,'method': 'GET'
            ,'path': '/locations'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'cache-control': 'max-age=0'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36)'
        })
        request = session.get(self.url)
        if request.status_code == 200:
            rows = html.fromstring(request.text).xpath('//div[@data-ux="ContentText"]')
            for row in rows:
                if xpath(row, './/span//text()') is None:
                    continue
                yield row


if __name__ == '__main__':
    s = Sandellasusa()
    s.run()
