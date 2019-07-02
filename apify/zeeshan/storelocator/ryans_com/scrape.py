import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Ryans(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'ryans.com'
    url = 'http://ryans.com/index.php'

    def map_data(self, row):
        
        obj = xpath(row, './/following-sibling::p')

        address = [o.strip() for o in obj.xpath('.//text()') if o.strip()]
        street_address, region, _, phone = address
        city, state_zip = region.split(',')
        state, zip = state_zip.strip().split(' ')

        url = xpath(obj, './/a/@href')

        coordinates = re.findall('[\-\d]{2,3}\.\d{7}', url)
        latitude = coordinates[0]
        longitude = coordinates[1]

        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/text()')
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zip
            ,'country_code': self.default_country
            ,'store_number': '<MISSING>'
            ,'phone': phone
            ,'location_type': '<MISSING>'
            ,'latitude': latitude
            ,'longitude': longitude
            ,'hours_of_operation': '<MISSING>'
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

        for state_id in range(1, 52):
            stores_url = '%s?usahtml5map_get_state_info=%s&map_id=0' % (self.url, state_id,)
            stores_page = session.post(stores_url)

            if stores_page.status_code == 200:

                try:
                    hxt = html.fromstring(stores_page.text)
                except etree.XMLSyntaxError:
                    # Bad html; continue 
                    continue 

                stores = hxt.xpath('//div[contains(@style, "color: white;text-align: center;border: solid")]')
                
                for store in stores:
                    yield store



if __name__ == '__main__':
    rs = Ryans()
    rs.run()
