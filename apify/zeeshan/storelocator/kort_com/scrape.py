import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Kort(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'kort.com'
    url = 'https://www.kort.com/data.asmx/GetOPLocations'

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/nickname/text()')
            ,'street_address': xpath(row, './/address/text()')
            ,'city': xpath(row, './/city/text()')
            ,'state': xpath(row, './/state/text()')
            ,'zip': xpath(row, './/zip/text()')
            ,'country_code': self.default_country
            ,'store_number': xpath(row, './/id/text()')
            ,'phone': xpath(row, './/phone/text()')
            ,'location_type': xpath(row, './/brand/text()')
            ,'naics_code': '<MISSING>'
            ,'latitude': xpath(row, './/latitude/text()')
            ,'longitude': xpath(row, './/longitude/text()')
            ,'hours_of_operation': '<MISSING>'
        }

    def crawl(self):
        session = requests.Session()
        for state in self.us_states:
            geo = self.get_geo(state.title())
            payload = {
                'state': ''
                ,'lat': geo['lat']
                ,'lng': geo['lng']
                ,'startIndex': 0
                ,'maxIndex': 50
                ,'services': ''
                ,'brand': ''
                ,'county': ''
                ,'allowServicesHours': True
                ,'brandOnly': False
                ,'filterPandO': '0'
            }
            r = session.post(self.url, data=payload)
            if r.status_code == 200:
                hxt = html.fromstring(r.text)
                for hospital in hxt.xpath('//hospital'):
                    yield hospital

if __name__ == '__main__':
    k = Kort()
    k.run()
