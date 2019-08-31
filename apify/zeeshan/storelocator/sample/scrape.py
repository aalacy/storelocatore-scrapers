import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Name(base.Base):

    csv_filename = 'data.csv'
    domain_name = '.com'
    url = ''

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('', '')
            ,'street_address': row.get('', '')
            ,'city': row.get('', '')
            ,'state': row.get('', '')
            ,'zip': row.get('', '')
            ,'country_code': row.get('', '')
            ,'store_number': row.get('', '')
            ,'phone': row.get('', '')
            ,'location_type': row.get('', '')
            ,'naics_code': None
            ,'latitude': row.get('', '')
            ,'longitude': row.get('', '')
            ,'hours_of_operation': None
        }

    def crawl(self):

        session = requests.Session()

        session.headers.update({
            'Accept': 'text/plain, */*; q=0.01'
            ,'Accept-Encoding': 'gzip, deflate'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Content-Length': '0'
            ,'Host': 'ryans.com'
            ,'Origin': 'http://ryans.com'
            ,'Referer': 'http://ryans.com/restaurants/'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like ,Gecko) Chrome/75.0.3770.100 Safari/537.36'
            ,'X-Requested-With': 'XMLHttpRequest'
        })



if __name__ == '__main__':
    n = Name()
    n.run()
