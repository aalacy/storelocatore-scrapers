import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class FitnessConnection(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'fitnessconnection.com'
    url = 'https://fitnessconnection.com/locations/'

    def map_data(self, row):

        street_address = xpath(row, './/span[@class="address-wrapper"]/div/a/text()[following-sibling::br]').strip()
        region = xpath(row, './/span[@class="address-wrapper"]/div/a/text()[preceding-sibling::br]').strip()

        city = xpath(row, './/span[@class="city"]/text()')

        address = '%s, %s' % (street_address, region)
        geo = self.get_geo(address)
        
        state, zipcode = region.split(',')[-1].split(' ')
        
        return {
            'locator_domain': self.domain_name
            ,'location_name': city
            ,'street_address': street_address
            ,'city': city 
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': '<MISSING>'
            ,'phone': xpath(row, './/span[@class="phone"]/text()')
            ,'location_type': '<MISSING>'
            ,'naics_code': '<MISSING>'
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': '<INACCESSIBLE>'
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'authority': 'fitnessconnection.com'
            ,'method': 'GET'
            ,'path': '/locations/'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'cache-control': 'max-age=0'
            ,'referer': 'https://fitnessconnection.com/'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        })
        request = session.get(self.url)
        if request.status_code == 200:
            hxt = html.fromstring(request.text)
            rows = hxt.xpath('//div[@class="club column small-12 medium-4"]')
            for row in rows:
                yield row


if __name__ == '__main__':
    fc = FitnessConnection()
    fc.run()
