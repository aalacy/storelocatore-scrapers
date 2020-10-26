import re 
import base
import random
import requests

from zipdata import zipdata

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Adidas(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'adidas.com'
    url = 'https://placesws.adidas-group.com/API/search'
    seen = set()

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('name', '')
            ,'street_address': row.get('street1', '')
            ,'city': row.get('city', '')
            ,'state': row.get('state', '')
            ,'zip': row.get('postal_code', '')
            ,'country_code': row.get('country', '')
            ,'store_number': row.get('id', '')
            ,'phone': None
            ,'location_type': row.get('storetype', '')
            ,'naics_code': None
            ,'latitude': row.get('latitude_google', '')
            ,'longitude': row.get('longitude_google', '')
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json, text/javascript, */*; q=0.01'
            ,'Origin': 'https://www.adidas.com'
            ,'Referer': 'https://www.adidas.com/us/storefinder'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        })
        for i, data in enumerate(zipdata):
            geo = self.get_geo(data.code)
            if geo is None: continue
            query_params = {
                'brand': 'adidas'
                ,'geoengine': 'google'
                ,'method': 'get'
                ,'category': 'store'
                ,'latlng': '%s,%s,%s' % (geo['lat'], geo['lng'], random.randint(10,69))
                ,'page': 1
                ,'pagesize': 500
                ,'fields': 'name,street1,street2,addressline,buildingname,postal_code,city,state,store_o wner,country,storetype,longitude_google,latitude_google,store_owner,state,performance,brand_store,factory_outlet,originals,neo_label,y3,slvr,children,woman,footwear,football,basketball,outdoor,porsche_design,miadidas,miteam,stella_mccartney,eyewear,micoach,opening_ceremony,operational_status,from_date,to_date,dont_show_country'
                ,'format': 'json'
                ,'storetype': ''
            }
            request = session.get(self.url, params=query_params)
            if request.status_code == 200:
                locations = request.json().get('wsResponse', {}).get('result', [])
                for location in locations:
                    if location.get('country') not in ('US', 'CA',): continue
                    store_number = location.get('id')
                    if store_number in self.seen: continue
                    else: self.seen.add(store_number)

                    print(store_number)

                    yield location


if __name__ == '__main__':
    a = Adidas()
    a.run()
