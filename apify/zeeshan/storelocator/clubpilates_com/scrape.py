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

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('title')
            ,'street_address': row.get('address')
            ,'city': row.get('city')
            ,'state': row.get('state')
            ,'zip': row.get('zip')
            ,'country_code': row.get('country')
            ,'store_number': row.get('ID')
            ,'phone': row.get('phone')
            ,'location_type': row.get('type')
            ,'naics_code': None
            ,'latitude': row.get('lat')
            ,'longitude': row.get('lng')
            ,'hours_of_operation': None
        }

    def crawl(self):
        ret = os.system('curl -XGET %s > data.json' % self.url)
        if ret == 0:
            with open('data.json', 'rb') as fp:
                data = fp.readlines()
                rows = eval(data[0]) if data else data
                for row in rows:
                    yield row


if __name__ == '__main__':
    cp = ClubPilates()
    cp.run()
