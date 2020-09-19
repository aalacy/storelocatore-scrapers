import re
import urllib.request, urllib.parse, urllib.error
import base
import requests

from pdb import set_trace as bp

class Valero(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'valero.com'
    url = 'https://valeromaps.valero.com/Home/Search'

    def map_data(self, row):
        address, city, state, zipcode = None, None, None, None
        address_split = re.findall('(.+) (.+), ([A-Z]{2}) ([0-9]{5}-[0-9]{4})', row['Address'])
        if address_split:
            address, city, state, zipcode = address_split[0]
        return {
            'locator_domain': self.domain_name
            ,'location_name': row['StationName']
            ,'street_address': address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': row['UniqueID']
            ,'phone': row['Phone']
            ,'location_type': 'Station'
            ,'naics_code': None
            ,'latitude': row['Latitude']
            ,'longitude': row['Longitude']
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.get('https://www.valero.com/en-us/Pages/StoreLocator.aspx')
        session.headers.update({
            'Accept': '*/*'
            ,'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            ,'Origin': 'https://valeromaps.valero.com'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
            ,'X-Requested-With': 'XMLHttpRequest'
        })
        payload = {
            'NEBound_Lat': '63.4087674107947'
            ,'NEBound_Long': '-36.02838131068279'
            ,'SWBound_Lat': '-5.227653565752919'
            ,'SWBound_Long': '-161.7723998653703'
            ,'center_Lat': '29.090556922520893'
            ,'center_Long': '-98.90039058802654'
        }
        query_params = {'SPHostUrl': urllib.parse.quote_plus('https://www.valero.com/en-us')}
        r = session.post(self.url, data=payload, params=query_params)
        if r.status_code == 200:
            for store in r.json()['StoreList']:
                yield store


if __name__ == '__main__':
    v = Valero()
    v.run()
