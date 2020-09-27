import re 
import json
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class RogersAndGollands(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'rogersandhollands.com'
    url = 'https://rogersandhollands.com/ustorelocator/location/map'

    def map_data(self, row):
        address = row.get('address')
        street_address, city, state, zipcode = None, None, None, None
        address =  re.findall(r'(.+), ([A-Z][a-z]+), ([A-Z]{2}) (\d{5})', address)
        if address:
            street_address, city, state, zipcode = address[0] 

        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('title', '')
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': row.get('country', '')
            ,'store_number': row.get('location_id', '')
            ,'phone': row.get('phone', '')
            ,'location_type': row.get('use_label', '')
            ,'naics_code': None
            ,'latitude': row.get('latitude', '')
            ,'longitude': row.get('longitude', '')
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'authority': 'rogersandhollands.com'
            ,'method': 'GET'
            ,'path': '/ustorelocator/location/map'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'referer': 'https://rogersandhollands.com/'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        })
        request = session.get(self.url)
        if request.status_code == 200:
            content = request.text
            data = re.findall(r'initial_locations:  (\[.+\])', content)
            rows = json.loads(data[0]) if data else None
            for row in rows:
                yield row


if __name__ == '__main__':
    rag = RogersAndGollands()
    rag.run()
