import requests
import csv
import datetime

class UmpquaBank:
    csv_filename = 'data.csv'
    domain_name = 'umpquabank.com'
    url = 'https://www.umpquabank.com/api/v1/locations'
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
            'content-type': 'application/json'
            ,'cache-control': 'max-age=0'
            ,'authority': 'www.umpquabank.com'
            ,'method': 'POST'
            ,'content-length': 185
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
        })
        api_data = {"latitude":37.7618242,"longitude":-122.39858709999999,"spanishSpeaking":False,"atm":False,"openNow":False,"openSaturdays":False,"driveUpWindow":False,"date":"2019-08-22T04:04:22.311Z"}
        r = session.post(self.url, json=api_data, allow_redirects=False)
        if r.status_code == 200:
            print(r.content)

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
