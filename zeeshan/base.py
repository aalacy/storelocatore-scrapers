import csv
from pdb import set_trace as bp

class Base(object):

    csv_filename = ''
    csv_fieldnames = ['locator_domain', 'location_name', 'street_address', 'city', 'state', 'zip', 'country_code', 'store_number', 'phone', 'location_type', 'naics_code', 'latitude', 'longitude', 'hours_of_operation']
    domain_name = ''
    default_country = 'US'
    url = ''
    headers = {
        'Accept-Encoding': 'gzip, deflate, br'
        ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
        ,'Connection': 'keep-alive'
        ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    }
    rows = []

    def write_to_csv(self):
        with open(self.csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_fieldnames)
            writer.writeheader()
            for row in self.rows:
                if hasattr(self, 'map_data'):
                    row = self.map_data(row)
                writer.writerow(row)
    
    def run(self):
        self.rows = self.crawl()
        self.write_to_csv()