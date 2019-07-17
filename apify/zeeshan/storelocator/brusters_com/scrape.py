import base
import requests

class Brusters(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'brusters.com'
    url = 'https://brusters.azurewebsites.net/API/AutoCompleteListJson.aspx'

    def map_data(self, row):
        address = row['address']
        geo = self.get_geo(address)
        return {
            'locator_domain': self.domain_name
            ,'location_name': row['name']
            ,'street_address': address
            ,'city': row['city']
            ,'state': row['state']
            ,'zip': row['zip']
            ,'country_code': self.default_country
            ,'store_number': row['number']
            ,'phone': None
            ,'location_type': None
            ,'naics_code': None
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json, text/javascript, */*; q=0.01'
            ,'Origin': 'https://brusters.com'
            ,'Referer': 'https://brusters.com/location-finder/?zip=Arrowhead%2C+Glendale%2C+AZ'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        })
        r = session.get(self.url)
        if r.status_code == 200:
            for store in r.json()['results']:
                yield store


if __name__ == '__main__':
    b = Brusters()
    b.run()
