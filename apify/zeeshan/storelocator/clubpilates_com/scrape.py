import os
import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class ClubPilates(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'clubpilates.com'
    url = 'https://www.clubpilates.com/wp-content/themes/clubpilates_v02_1/actions/preOpen_get_locations.php'
    seen = set()

    def map_data(self, row):
        zipcode = row.get('zip').strip()
        if len(zipcode) == 6:
            zipcode = zipcode[:3] + ' ' + zipcode[3:]
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('title')
            ,'street_address': row.get('address')
            ,'city': row.get('city')
            ,'state': row.get('state')
            ,'zip': zipcode
            ,'country_code': row.get('country')
            ,'store_number': row.get('ID')
            ,'phone': row.get('phone') if len(row.get('phone')) >= 10 else None
            ,'location_type': row.get('type')
            ,'naics_code': '<MISSING>'
            ,'latitude': row.get('lat')
            ,'longitude': row.get('lng')
            ,'hours_of_operation': '<MISSING>'
        }

    def crawl(self):
        ret = os.system('curl -XGET %s > data.json' % self.url)
        if ret == 0:
            with open('data.json', 'rb') as fp:
                data = fp.readlines()
                rows = eval(data[0]) if data else data
                for row in rows:
                    store_number = row.get('ID')
                    if store_number in self.seen: continue
                    else: self.seen.add(store_number)
                    yield row


if __name__ == '__main__':
    cp = ClubPilates()
    cp.run()
