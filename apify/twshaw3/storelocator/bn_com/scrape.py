import usaddress
import re 
from sgrequests import SgRequests
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
import csv
import sgzip

from lxml import (html, etree,)

class BarnesandNoble:
    csv_filename = ''
    csv_fieldnames = ['locator_domain', 'location_name', 'street_address', 'city', 'state', 'zip', 'country_code', 'store_number', 'phone', 'location_type', 'latitude', 'longitude', 'hours_of_operation']
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

    def parse_address(self, store_data_1, store_data_2):
        zip_code = store_data_2[-5:]
        state = store_data_2.split(",")[-1][0:-5].strip()
        city = '<MISSING>'
        address = '<MISSING>'
        if not store_data_2[0].isdigit() and any(char.isdigit() for char in store_data_1):
            address = store_data_1
            city = store_data_2.split(',')[0].strip()
        else:
            try:
                tagged = usaddress.tag(store_data_2)[0]
                city = tagged['PlaceName'].strip()
                address = store_data_2[0:store_data_2.rfind(city)-1].strip()
            except:
                print("exception tagging address: " + store_data_2)

        return { 'zip': zip_code, 'state': state, 'city': city, 'address': address }

    def map_data(self, row):
        
        text = etree.tostring(row)
        store_data = text.split('</a> ')[1].split('<br/>')[0:3]

        phone = store_data[-1].strip().replace(' (main)', '')       
        
        parsed = self.parse_address(store_data[0].strip(), store_data[1].strip())

        return {
            'locator_domain': self.domain_name
            ,'location_name': self.xpath(row, './/h5[@class="nonoS"]//text()')
            ,'street_address': parsed['address']
            ,'city': parsed['city']
            ,'state': parsed['state']
            ,'zip': parsed['zip']
            ,'country_code': self.default_country
            ,'store_number': self.get_store_id(row)
            ,'phone': phone
            ,'location_type': '<MISSING>'
            ,'latitude': '<MISSING>'
            ,'longitude': '<MISSING>'
            ,'hours_of_operation': '<MISSING>'
        }

    def crawl(self):
        session = SgRequests()
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
        fs = [ executor.submit(self.crawl_zip_code, code, session) for code in sgzip.for_radius(50) ]
        wait(fs)
        executor.shutdown(wait=False)

        for unique_location in self.unique_locations:    
            yield unique_location

    def crawl_zip_code(self, code, session):
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

                self.unique_locations.append(location)

    def run(self):
        rows = self.crawl()
        self.write_to_csv(rows)

if __name__ == '__main__':
    bn = BarnesandNoble()
    bn.run()
