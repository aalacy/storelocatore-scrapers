import re
import base
import json
import requests
from pdb import set_trace as bp

class MacCosmetics(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'maccosmetics.com'
    url = 'https://m.maccosmetics.com/stores'

    def map_data(self, row):
        for key, value in row.items():
            if row[key] and hasattr(row[key], 'encode'):
                row[key] = value
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('DOORNAME')
            ,'street_address': row.get('ADDRESS')
            ,'city': row.get('CITY')
            ,'state': row.get('STATE_OR_PROVINCE')
            ,'zip': row.get('ZIP_OR_POSTAL')
            ,'country_code': row.get('COUNTRY')
            ,'store_number': row.get('DOOR_ID')
            ,'phone': row.get('PHONE1')
            ,'location_type': row.get('STORE_TYPE')
            ,'naics_code': None 
            ,'latitude': row.get('LATITUDE')
            ,'longitude': row.get('LONGITUDE')
            ,'hours_of_operation': None
        }

    def crawl(self):

        session = requests.Session()

        session.headers.update({
            'authority': 'm.maccosmetics.com'
            ,'method': 'GET'
            ,'path': '/stores'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'referer': 'https://m.maccosmetics.com/'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        })

        stores_page = session.get(self.url, headers=self.headers)

        if stores_page.status_code == 200:
            text = stores_page.text
            location_data = re.findall(r'site\.locator\.locationData = (.+);', text)
            
            if location_data:
                
                location_data = eval(location_data[0])

                ID = 1

                for country in ['USA', 'Canada']:

                    cities = ','.join([','.join(list(state.keys())) for state in list(location_data[country].values())]).split(',')
                    
                    for city in cities:

                        address = '%s, %s' % (city, country,)
                        geo = self.get_geo(address=address)

                        session.headers.update({
                            'authority': 'm.maccosmetics.com'
                            ,'method': 'POST'
                            ,'path': '/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents'
                            ,'scheme': 'https'
                            ,'accept': '*/*'
                            ,'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
                            ,'origin': 'https://m.maccosmetics.com'
                            ,'referer': 'https://m.maccosmetics.com/stores'
                            ,'x-requested-with': 'XMLHttpRequest'
                        })

                        payload = {'JSONRPC': [{"method":"locator.doorsandevents","id":ID,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, SUB_HEADING, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, PHONE2, STORE_TYPE, LONGITUDE, LATITUDE, COMMENTS","country":"United States","latitude":geo['lat'],"longitude":geo['lng'],"region_id":0,"radius":100}]}]}

                        payload = {'JSONRPC': json.dumps([{"method":"locator.doorsandevents","id":ID,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, SUB_HEADING, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, PHONE2, STORE_TYPE, LONGITUDE, LATITUDE, COMMENTS","country":"United States","latitude":geo['lat'],"longitude":geo['lng'],"region_id":0,"radius":100}]}])}

                        search = session.post('https://m.maccosmetics.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents', data=payload)

                        ID = ID + 1

                        results = search.json()[0]['result']['value'].get('results', {})
                        stores = list(results.values())

                        for store in stores:
                            yield store

if __name__ == '__main__':
    mc = MacCosmetics()
    mc.run()
