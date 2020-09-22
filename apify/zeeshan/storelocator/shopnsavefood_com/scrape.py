import base 
import requests
from pdb import set_trace as bp

class ShopnSaveFood(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'shopnsavefood.com'
    default_country = 'US'
    url = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores'

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
        self.headers.update({
            'Accept': 'application/json, text/plain, */*'
            ,'Content-Type': 'application/json; charset=utf-8'
            ,'Host': 'www.shopnsavefood.com'
            ,'Referer': 'https://www.shopnsavefood.com/locations'
        })
        r = requests.get(self.url, headers=self.headers)
        if r.status_code == 200:
            json = r.json()
            rows = json['d']
            return rows

if __name__ == '__main__':
    ssf = ShopnSaveFood()
    ssf.run()
