import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class BlueWaterStores(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'bluewaterstores.com'
    url = 'http://www.bluewaterstores.com/wp-content/plugins/store-locator/sl-xml.php'

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('name')
            ,'street_address': row.get('street')
            ,'city': row.get('city') 
            ,'state': row.get('state')
            ,'zip': row.get('zip')
            ,'country_code': self.default_country
            ,'store_number': '<MISSING>'
            ,'phone': row.get('phone')
            ,'location_type': '<MISSING>'
            ,'naics_code': '<MISSING>'
            ,'latitude': row.get('lat')
            ,'longitude': row.get('lng')
            ,'hours_of_operation': '<MISSING>'
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept': '*/*'
            ,'Accept-Encoding': 'gzip, deflate'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Host': 'www.bluewaterstores.com'
            ,'Referer': 'http://www.bluewaterstores.com/stores/'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        })
        request = session.get(self.url)
        if request.status_code == 200:
            hxt = html.fromstring(request.text)
            rows = hxt.xpath('//marker')
            for row in rows:
                yield row


if __name__ == '__main__':
    bws = BlueWaterStores()
    bws.run()
