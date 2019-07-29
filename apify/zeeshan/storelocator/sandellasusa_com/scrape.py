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
        street_address = xpath(row, './/p[3]//span/text()').strip()

        city, state, zipcode = None, None, None
        region = re.findall(r'([A-Za-z]+), ([A-Z]+) ([0-9]+)', text)
        if region:
            city, state, zipcode = region[0]

        phone = re.findall(r'\d+-\d+-\d+', text)
        phone = phone[0] if phone else None

        address = '%s, %s' % (street_address, region)
        geo = self.get_geo(address)

        return {
            'locator_domain': self.domain_name
            ,'location_name': name
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': None
            ,'phone': phone
            ,'location_type': None
            ,'naics_code': None
            ,'latitude': geo.get('lat', '')
            ,'longitude': geo.get('lng', '')
            ,'hours_of_operation': None
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
