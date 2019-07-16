import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class FarmerBoys(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'farmerboys.com'
    url = 'https://www.farmerboys.com/locations/'

    def map_data(self, row):
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('restaurant_name', '<MISSING>')
            ,'street_address': row.get('location_address1', '<MISSING>')
            ,'city': row.get('location_city', '<MISSING>')
            ,'state': row.get('location_state', '<MISSING>')
            ,'zip': row.get('location_zip', '<MISSING>')
            ,'country_code': self.default_country
            ,'store_number': row.get('corporate_location', '<MISSING>')
            ,'phone': row.get('phone_primary', '<MISSING>')
            ,'location_type': '<MISSING>'
            ,'naics_code': '<MISSING>'
            ,'latitude': row.get('geo_latitude', '<MISSING>')
            ,'longitude': row.get('geo_longitude', '<MISSING>')
            ,'hours_of_operation': row.get('store_hours', '<MISSING>')
        }

    def crawl(self):

        keys = [
            'restaurant_id',
            'restaurant_name',
            'location_address1',
            'location_address2',
            'location_city',
            'location_state',
            'location_zip',
            'geo_latitude',
            'geo_longitude',
            'phone_primary',
            'phone_catering',
            'phone_fax',
            'store_hours',
            'web_url',
            'location_pic',
            'option_wifi',
            'loyalty_club',
            'corporate_location',
        ]
        session = requests.Session()
        session.headers.update({
            'authority': 'www.farmerboys.com'
            ,'method': 'GET'
            ,'path': '/locations/'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'cache-control': 'max-age=0'
            ,'referer': 'https://www.farmerboys.com/'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        })
        r = session.get(self.url)
        if r.status_code == 200:

            hxt = html.fromstring(r.text)
            script = xpath(hxt, '//div[@class="entry-content"]//script//text()')
            script = re.sub('\s+', ' ', script)
            result = re.findall(r'(\[.*\])', script)
            if result:
                result = result[0]
                for key in keys:
                    result = result.replace(key, '"%s"' % key)
                data = eval(result)
                for row in data:
                    yield row


if __name__ == '__main__':
    fb = FarmerBoys()
    fb.run()
