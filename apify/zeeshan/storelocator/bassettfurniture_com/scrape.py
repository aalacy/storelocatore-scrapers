import base 
import time
import json
import urllib
import requests

class BassettFurniture(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'bassettfurniture.com'
    url = 'https://bassett.brickworksoftware.com/locations_search'

    def map_data(self, row):
        attributes = row.get('attributes', {})
        geo = row.get('_geoloc', {})
        return {
            'locator_domain': row.get('domain')
            ,'location_name': attributes.get('name')
            ,'street_address': attributes.get('address1')
            ,'city': attributes.get('city')
            ,'state': attributes.get('state')
            ,'zip': attributes.get('postalCode') 
            ,'country_code': attributes.get('countryCode')
            ,'store_number': row.get('id')
            ,'phone': attributes.get('phoneNumber') 
            ,'location_type': attributes.get('type')
            ,'naics_code': None 
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': None
        }

    def crawl(self):
        
        self.headers.update({
            'Accept': 'application/json, text/plain, */*'
            ,'Origin': 'https://www.bassettfurniture.com'
        })
        
        page, now = 0, int(time.time()*1000)

        esSearch = {
            "page": 0
            ,"storesPerPage": 50
            ,"domain": "bassett.brickworksoftware.com"
            ,"locale": "en_US"
            ,"must": [
                {
                    "type": "range"
                    ,"field": "published_at"
                    ,"value" : {
                        "lte": now
                    }
                }
            ]
            ,"filters": []
            ,"aroundLatLngViaIP": True
        }

        query_params = {
            'page': 0
            ,'getRankingInfo': True
            ,'facets[]': '*'
            ,'aroundRadius': 'all'
            ,'filters': 'domain:bassett.brickworksoftware.com AND publishedAt<=%d' % now
            ,'esSearch': json.dumps(esSearch)
            ,'aroundLatLngViaIP': True
        }
        
        request = requests.get(self.url, params=query_params, headers=self.headers)
        
        if request.status_code == 200:
            obj = request.json()
            pages = obj['nbPages']
            rows = obj['hits']
            while page < pages:
                page += 1
                query_params['page'] = page
                esSearch['page'] = page
                query_params['esSearch'] = json.dumps(esSearch)
                request = requests.get(self.url, params=query_params, headers=self.headers)
                if request.status_code == 200:
                    obj = request.json()
                    rows.extend(obj['hits'])
            return rows

if __name__ == '__main__':
    bf = BassettFurniture()
    bf.run()
