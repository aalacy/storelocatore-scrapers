import re 
import base
import requests

from zipdata import zipdata

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Wendys(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'wendys.com'
    url = 'https://locationservices.wendys.com/LocationServices/rest/nearbyLocations'
    seen = set()

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('name', '')
            ,'street_address': row.get('address1', '')
            ,'city': row.get('city', '')
            ,'state': row.get('state', '')
            ,'zip': row.get('postal', '') if len(row.get('postal', '')) <= 6 else None
            ,'country_code': row.get('country', '')
            ,'store_number': row.get('id', '')
            ,'phone': row.get('phone', '') if len(row.get('phone', '')) >= 10 else None
            ,'location_type': row.get('utcOffset', '')
            ,'naics_code': None
            ,'latitude': row.get('lat', '')
            ,'longitude': row.get('lng', '')
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
        for data in zipdata:
            query_params = {
                'lang': 'en'
                ,'cntry': 'US'
                ,'sourceCode': 'FIND.WENDYS'
                ,'version': '5.22.0'
                ,'address': data.code
                ,'limit': 25
                ,'radius': 20
            }
            r = session.get(self.url, params=query_params)
            if r.status_code == 200:
                for row in r.json().get('data', []):
                    if row['id'] in self.seen: continue
                    else: self.seen.add(row['id'])
                    yield row


if __name__ == '__main__':
    w = Wendys()
    w.run()
