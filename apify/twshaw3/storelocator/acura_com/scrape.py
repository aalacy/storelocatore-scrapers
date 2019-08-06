import re 
import requests
import csv

from lxml import (html, etree,)

class Acura:
    csv_filename = 'data.csv'
    domain_name = 'acura.com'
    url = 'https://www.acura.com/platform/api/v1/dealer'
    seen = set()
    csv_fieldnames = ['locator_domain', 'location_name', 'street_address', 'city', 'state', 'zip', 'country_code', 'store_number', 'phone', 'location_type', 'latitude', 'longitude', 'hours_of_operation']
    domain_name = ''
    default_country = 'US'

    def write_to_csv(self, rows):
        output_file = self.csv_filename
        with open(output_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_fieldnames)
            writer.writeheader()
            for row in rows:
                if hasattr(self, 'map_data'):
                    row = self.map_data(row)
                writer.writerow(row)

    def get_zips(self):
        with open('zips.csv', 'rb') as f:
            reader = csv.reader(f)
            return list(reader)

    def map_data(self, row):
        missing = '<MISSING>'
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('Name', missing)
            ,'street_address': row.get('Address', missing)
            ,'city': row.get('City', missing)
            ,'state': row.get('State', missing)
            ,'zip': row.get('ZipCode', missing)
            ,'country_code': self.default_country
            ,'store_number': row.get('DealerNumber', missing)
            ,'phone': row.get('Phone', missing)
            ,'location_type': ', '.join([attr['Code'] for attr in row.get('Attributes', [])])
            ,'latitude': row.get('Latitude', missing)
            ,'longitude': row.get('Longitude', missing)
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

        for code in self.get_zips():
            print(code)
            previous_zip_code = code
            query_params = {
                'productDivisionCode': 'B'
                ,'getDDPOnly': False
                ,'zip': code
                ,'maxResults': 100
            }
            session.headers.update({
                'referer': 'https://www.acura.com/dealer-locator-inventory?zipcode=%s' % previous_zip_code
                ,'path': '/platform/api/v1/dealer?productDivisionCode=B&getDDPOnly=false&zip=%s&maxResults=%s' % (code, 100,)
            })
            request = session.get(self.url, params=query_params)
            if request.status_code == 200:
                locations = request.json().get('Dealers', [])
                if locations:
                    for location in locations:
                        store_number = location.get('DealerNumber')
                        if store_number in self.seen: continue
                        else: self.seen.add(store_number)
                        yield location

    def run(self):
        rows = self.crawl()
        self.write_to_csv(rows)

if __name__ == '__main__':
    a = Acura()
    a.run()
