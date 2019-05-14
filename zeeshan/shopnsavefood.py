import csv
import requests 
from pdb import set_trace as bp

class ShopnSaveFood(object):

    csv_filename = 'shopnsavefood.csv'
    csv_fieldnames = ['locator_domain', 'location_name', 'street_address', 'city', 'state', 'zip', 'country_code', 'store_number', 'phone', 'location_type', 'naics_code', 'latitude', 'longitude', 'hours_of_operation']
    domain_name = 'shopnsavefood.com'
    default_country = 'US'
    url = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores'
    headers = {
        'Accept': 'application/json, text/plain, */*'
        ,'Accept-Encoding': 'gzip, deflate, br'
        ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
        ,'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.3'
        ,'Connection': 'keep-alive'
        ,'Content-Type': 'application/json; charset=utf-8'
        ,'Host': 'www.shopnsavefood.com'
        ,'Referer': 'https://www.shopnsavefood.com/locations'
        ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    }
    json = {}

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': None
            ,'street_address': row.get('Address1')
            ,'city': row.get('City')
            ,'state': row.get('State')
            ,'zip': row.get('Zip') 
            ,'country_code': self.default_country
            ,'store_number': row.get('StoreID')
            ,'phone': None
            ,'location_type': 'Gas Station' if row.get('IsGasStation', False) else None
            ,'naics_code': None 
            ,'latitude': row.get('Latitude')
            ,'longitude': row.get('Longitude')
            ,'hours_of_operation': None
        }

    def crawl(self):
        r = requests.get(self.url, headers=self.headers)
        if r.status_code == 200:
            self.json = r.json()

    def write_to_csv(self):
        with open(self.csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_fieldnames)
            writer.writeheader()
            for row in self.json['d']:
                row = self.map_data(row)
                writer.writerow(row)

    def run(self):
        self.crawl()
        self.write_to_csv()

if __name__ == '__main__':
    ssf = ShopnSaveFood()
    ssf.run()
