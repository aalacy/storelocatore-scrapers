import re 
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
import csv

from lxml import (html, etree,)

class BarnesandNoble:
    csv_filename = ''
    csv_fieldnames = ['locator_domain', 'location_name', 'street_address', 'city', 'state', 'zip', 'country_code', 'store_number', 'phone', 'location_type', 'naics_code', 'latitude', 'longitude', 'hours_of_operation']
    domain_name = ''
    default_country = 'US'

    def write_to_csv(self, rows):
        output_file = self.csv_filename
        with open(output_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_fieldnames)
            writer.writeheader()
            for row in rows:
                row = self.map_data(row)
                writer.writerow(row)

    def xpath(self, hxt, query_string):
        hxp = hxt.xpath(query_string)
        if hxp:
            if hasattr(hxp[0], 'encode'):
                return hxp[0].encode('ascii', 'ignore')
            return hxp[0]
        return None

    def get_zips(self):
        import csv
        with open('zips.csv', 'rb') as f:
            reader = csv.reader(f)
            return list(reader)

    csv_filename = 'data.csv'
    domain_name = 'bn.com'
    url = 'https://mstores.barnesandnoble.com/stores'
    seen = set()
    unique_locations = []

    def get_store_id(self, location):
        store_id = self.xpath(location, './/a/@href')
        store_id = re.findall(r'[0-9]+', store_id)
        store_id = store_id[0] if store_id else None
        return store_id

    def map_data(self, row):
        
        text = etree.tostring(row)

        street_address = etree.tostring(self.xpath(row, './/h5[@class="nonoS"]//parent::*'))
        if street_address:
            street_address = street_address.split('</a> ')[-1]

        phone = re.findall(r'\d{3}-\d{3}-\d{4}', text)
        phone = phone[0] if phone else None

        city, state, zip_code = row.get('city'), row.get('state'), row.get('zip')

        address = '%s, %s, %s %s' % (street_address, city, state, zip_code)

        return {
            'locator_domain': self.domain_name
            ,'location_name': self.xpath(row, './/h5[@class="nonoS"]//text()')
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zip_code
            ,'country_code': self.default_country
            ,'store_number': self.get_store_id(row)
            ,'phone': phone
            ,'location_type': None
            ,'naics_code': None
            ,'latitude': None
            ,'longitude': None
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Host': 'mstores.barnesandnoble.com'
            ,'Referer': 'https://mstores.barnesandnoble.com/stores'
            ,'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

        })
        executor = ThreadPoolExecutor(max_workers=10)
        fs = [ executor.submit(self.crawl_zip_code, code, session) for code in self.get_zips() ]
        wait(fs)

        for unique_location in self.unique_locations:    
            yield unique_location

    def crawl_zip_code(self, code, session):
        print(code)
        query_params = {
            'page': None
            ,'size': 100
            ,'searchText': code
            ,'storeFilter': 'all'
            ,'view': 'list'
            ,'v': 1
        }
        request = session.get(self.url, params=query_params)
        if request.status_code == 200:
            hxt = html.fromstring(request.text)
            locations = hxt.xpath('//div[@class="col-sm-12 col-md-8 col-lg-8 col-xs-12"]')
            for location in locations:
                store_id = self.get_store_id(location)

                if store_id in self.seen: continue
                else: self.seen.add(store_id)
                        
                location.attrib['city'] = ''#data.city
                location.attrib['state'] = ''#data.state
                location.attrib['zip'] = ''#data.code
                self.unique_locations.append(location)

    def run(self):
        rows = self.crawl()
        self.write_to_csv(rows)

if __name__ == '__main__':
    bn = BarnesandNoble()
    bn.run()
