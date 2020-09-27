import re
import json 
import base
import random
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Providence(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'providence.org'
    url = 'https://www.providence.org/location-directory'

    def map_data(self, row):

        street_address, city, state, zipcode = ('', '', '', '',)

        address = row['Address'].split('<br/>')
        street_address = ', '.join(address[:-1])
        region = address[-1]
        if region:
            city, state_zip = region.split(',')
            state_zip = re.sub(r'\s+', ' ', state_zip).strip()
            state, zipcode = state_zip.split(' ')

        return {
            'locator_domain': self.domain_name
            ,'location_name': row['Name']
            ,'street_address': street_address.strip()
            ,'city': city.strip()
            ,'state': state.strip()
            ,'zip': zipcode.strip()
            ,'country_code': self.default_country
            ,'store_number': None
            ,'phone': row['PhoneNumber']
            ,'location_type': row['GroupType']
            ,'naics_code': None
            ,'latitude': row['Latitude']
            ,'longitude': row['Longitude']
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'authority': 'www.providence.org'
            ,'method': 'GET'
            ,'path': '/location-directory'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'cache-control': 'max-age=0'
            ,'referer': 'https://www.providence.org/'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        })
        r1 = session.get(self.url)
        if r1.status_code == 200:
            hxt1 = html.fromstring(r1.text)
            states = hxt1.xpath('//a[contains(text(), "All locations")]/@href')
            for state_url in states:
                url = '%s/list-view?within=5000' % state_url
                r2 = session.get(url)
                if r2.status_code == 200:
                    hxt2 = html.fromstring(r2.text)
                    script = xpath(hxt2, '//script[contains(text(), "locationsList =")]/text()')
                    
                    if script is None: continue

                    script = script.replace('locationsList = \'', '')
                    script = script.replace('\';', '')
                    locations = json.loads(script)
                    for row in locations:
                        group_type, latitude, longitude = row['GroupType'], row['Latitude'], row['Longitude']
                        for location in row['Locations']:
                            location['GroupType'] = group_type
                            location['Latitude'] = latitude
                            location['Longitude'] = longitude
                            yield location


if __name__ == '__main__':
    p = Providence()
    p.run()
