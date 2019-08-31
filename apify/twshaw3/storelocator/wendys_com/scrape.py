import requests
import csv

class Wendys:
    csv_filename = 'data.csv'
    domain_name = 'wendys.com'
    url = 'https://locationservices.wendys.com/LocationServices/rest/nearbyLocations'
    seen = set()
    csv_fieldnames = ['locator_domain', 'location_name', 'street_address', 'city', 'state', 'zip', 'country_code', 'store_number', 'phone', 'location_type', 'latitude', 'longitude', 'hours_of_operation']

    def encode(self, string):
        return string.encode('utf-8')

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': self.encode(row.get('name', '<MISSING>'))
            ,'street_address': self.encode(row.get('address1', '<MISSING>'))
            ,'city': self.encode(row.get('city', '<MISSING>'))
            ,'state': self.encode(row.get('state', '<MISSING>'))
            ,'zip': self.encode(row.get('postal', '<MISSING>')) if len(row.get('postal', '')) <= 6 else None
            ,'country_code': self.encode(row.get('country', '<MISSING>'))
            ,'store_number': self.encode(row.get('id', '<MISSING>'))
            ,'phone': self.encode(row.get('phone', '<MISSING>')) if len(row.get('phone', '')) >= 10 else None
            ,'location_type': row.get('utcOffset', '<MISSING>')
            ,'latitude': row.get('lat', '<MISSING>')
            ,'longitude': row.get('lng', '<MISSING>')
            ,'hours_of_operation': ', '.join('%s-%s; day %d' % (d.get('openTime'), d.get('closeTime'), d.get('day')) for d in row.get('daysOfWeek', ''))
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json'
            ,'cache-control': 'no-cache'
            ,'Content-Type': 'application/json'
            ,'Origin': 'https://find.wendys.com'
            ,'Referer': 'https://find.wendys.com/'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        })
        query_params = {
            'lang': 'en'
            ,'cntry': 'US'
            ,'sourceCode': 'FIND.WENDYS'
            ,'version': '5.22.0'
            ,'address': '94107'
            ,'limit': 100000
            ,'radius': 13000
        }
        r = session.get(self.url, params=query_params)
        if r.status_code == 200:
            for row in r.json().get('data', []):
                if row['id'] in self.seen: continue
                else: self.seen.add(row['id'])
                yield row

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
    w = Wendys()
    w.run()
