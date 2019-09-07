import re 
import base
import requests

from zipdata import zipdata

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Acura(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'acura.com'
    url = 'https://www.acura.com/platform/api/v1/dealer'
    seen = set()

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('Name', '')
            ,'street_address': row.get('Address', '')
            ,'city': row.get('City', '')
            ,'state': row.get('State', '')
            ,'zip': row.get('ZipCode', '')
            ,'country_code': self.default_country
            ,'store_number': row.get('DealerNumber', '')
            ,'phone': row.get('Phone', '')
            ,'location_type': ', '.join([attr['Code'] for attr in row.get('Attributes', [])])
            ,'naics_code': None
            ,'latitude': row.get('Latitude', '')
            ,'longitude': row.get('Longitude', '')
            ,'hours_of_operation': ', '.join(['%s-%s' % (hour['Days'], hour['Hours']) for hour in row.get('SalesHours', [])])
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'authority': 'www.acura.com'
            ,'method': 'GET'
            ,'scheme': 'https'
            ,'accept': 'application/json, text/plain, */*'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        })

        previous_zip_code = 90001

        for data in zipdata:
            previous_zip_code = data.code
            query_params = {
                'productDivisionCode': 'B'
                ,'getDDPOnly': False
                ,'zip': data.code
                ,'maxResults': 100
            }
            session.headers.update({
                'referer': 'https://www.acura.com/dealer-locator-inventory?zipcode=%s' % previous_zip_code
                ,'path': '/platform/api/v1/dealer?productDivisionCode=B&getDDPOnly=false&zip=%s&maxResults=%s' % (data.code, 100,)
            })
            request = session.get(self.url, params=query_params)
            if request.status_code == 200:
                locations = request.json().get('Dealers', [])
                for location in locations:
                    store_number = location.get('DealerNumber')
                    if store_number in self.seen: continue
                    else: self.seen.add(store_number)
                    yield location


if __name__ == '__main__':
    a = Acura()
    a.run()
