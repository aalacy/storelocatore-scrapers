from sgrequests import SgRequests
import csv
import datetime
import sgzip
import geopy.distance
import random

class UmpquaBank:
    csv_filename = 'data.csv'
    domain_name = 'umpquabank.com'
    url = 'https://www.umpquabank.com/api/v1/locations'
    seen = set()
    csv_fieldnames = ['locator_domain', 'location_name', 'street_address', 'city', 'state', 'zip', 'country_code', 'store_number', 'phone', 'location_type', 'latitude', 'longitude', 'hours_of_operation']
    search = sgzip.ClosestNSearch()
    search.initialize()
    random.seed(1234)

    def encode(self, string):
        return string.encode('utf-8')

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': '<MISSING>'
            ,'street_address': self.encode(row.get('addressLine1', '<MISSING>'))
            ,'city': self.encode(row.get('city', '<MISSING>'))
            ,'state': self.encode(row.get('state', '<MISSING>'))
            ,'zip': self.encode(row.get('zip', '<MISSING>'))
            ,'country_code': 'US'
            ,'store_number': self.encode(row.get('storeNumber', '<MISSING>'))
            ,'phone': self.encode(row.get('phoneNumber', '<MISSING>'))
            ,'location_type': 'ATM' if row['atm'] else 'BRANCH'
            ,'latitude': row.get('latitude', '<MISSING>')
            ,'longitude': row.get('longitude', '<MISSING>')
            ,'hours_of_operation': '<MISSING>'
        }

    def crawl(self):
        session = SgRequests()
        headers = {
            'content-type': 'application/json'
            ,'cache-control': 'max-age=0'
            ,'authority': 'www.umpquabank.com'
            ,'method': 'POST'
            ,'path': '/api/v1/locations'
            ,'scheme': 'https'
            ,'accept': '*/*'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9'
            ,'origin': 'https://www.umpquabank.com/'
            ,'referer': 'https://www.umpquabank.com/'
            ,'sec-fetch-mode': 'cors'
            ,'sec-fetch-site': 'same-origin'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        query_coord = self.search.next_coord()
        locations = []
        while query_coord:
            print("remaining zipcodes: " + str(self.search.zipcodes_remaining()))
            lat, lng = query_coord[0], query_coord[1]
            api_data = {"latitude":lat,"longitude":lng,"spanishSpeaking":False,"atm":False,"openNow":False,"openSaturdays":False,"driveUpWindow":False,"date":"2019-08-22T04:04:22.311Z"}
            r = session.post(self.url, json=api_data, allow_redirects=False, headers=headers)
            if r.status_code == 200:
                json = r.json()
                result_coords = []
                for location in json['locations']:
                    result_coords.append((location['latitude'], location['longitude']))
                    if location['storeNumber'] not in self.seen:
                        self.seen.add(location['storeNumber'])
                        locations.append(location)
                self.search.max_count_update(result_coords)
                query_coord = self.search.next_coord()
        for loc in locations:
            yield loc

    def write_to_csv(self, rows):
        output_file = self.csv_filename
        with open(output_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_fieldnames)
            writer.writeheader()
            for row in rows:
                if hasattr(self, 'map_data'):
                    row = self.map_data(row)
                writer.writerow(row)

    def run(self):
        rows = self.crawl()
        self.write_to_csv(rows)

if __name__ == '__main__':
    w = UmpquaBank()
    w.run()
