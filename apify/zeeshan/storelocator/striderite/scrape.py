import re
import base 
import requests
import urllib

from lxml import html
from pdb import set_trace as bp

xpath = base.xpath

class StrideTite(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'striderite.com'
    url = 'https://www.striderite.com/en/stores'

    def _map_data(self, row):

        location_name = row.xpath('.//div[@class="store-name"]//span//text()')
        location_name = re.sub('\s+', ' ', location_name[0]).strip() if location_name else None

        store_number = row.xpath('.//div[@class="store-name"]//a//@id')
        store_number = store_number[0] if store_number else None

        geo = row.xpath('.//div[@class="store-name"]//a//@data-location')
        geo = eval(geo[0]) if geo else None

        address = row.xpath('.//td[@class="store-address"]/text()')
        address = [re.sub('\s+', ' ', line).strip() for line in address]

        street_address, city, state, postal_code = None, None, None, None
        country_code = None

        if len(address) == 5:
            street_address = '\n'.join(address[:2])
        else:
            street_address = address[0]

        country_code = address[-2]

        city, region = address[-3].split(',')
        city = city.strip()
        
        state = re.findall(r'[A-Za-z]+', region)
        postal_code = re.findall(r'[0-9]{5}', region)

        state = state[0] if state else None
        postal_code = postal_code[0] if postal_code else None
        
        phone = row.xpath('.//td[@class="store-phone"]//text()')
        phone = phone[0] if phone else None

        return {
            'locator_domain': self.domain_name
            ,'location_name': location_name
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': postal_code
            ,'country_code': country_code
            ,'store_number': store_number
            ,'phone': phone
            ,'location_type': None
            ,'naics_code': None 
            ,'latitude': geo.get('latitude', None)
            ,'longitude': geo.get('longitude', None)
            ,'hours_of_operation': None
        }

    def crawl(self):

        session = requests.Session()

        self.headers.update({
            'authority': 'www.striderite.com'
            ,'method': 'POST'
            ,'scheme': 'https'
            ,'accept': 'text/html, */*; q=0.01'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'content-type': 'application/x-www-form-urlencoded'
            ,'origin': 'https://www.striderite.com'
            ,'referer': 'https://www.striderite.com/en/stores?dwcont='
            ,'x-requested-with': 'XMLHttpRequest'
        })
        query_params = {
            'distanceMax': 10000 # this would cover all of the US!
            ,'zip': '63101' # Misouri zip; choose a near-center-most zip code
            ,'distanceUnit': 'mi'
            ,'country': 'US'
            ,'formType': 'findbyzipandcountry'
            ,'sz': 25 # max page size; obtained through trial-and-error
            ,'start': 0
        }
        payload = {'format': 'ajax'}

        session.headers.update(self.headers)

        r = session.post(self.url, params=query_params, data=payload)
        
        if r.status_code == 200:

            hxt = html.fromstring(r.text)

            for row in hxt.xpath('//table[@id="store-location-results"]//tr'):
                yield self._map_data(row)

            next_page = self.get_next_page(hxt)
            
            while next_page:
                url = xpath(next_page[0], '@href')
                
                query_params = base.query_params(url)
                start = query_params['start']

                r = session.post(url, data=payload)
                
                if r.status_code == 200:

                    hxt = html.fromstring(r.text)

                    for row in hxt.xpath('//table[@id="store-location-results"]//tr'):
                        yield self._map_data(row)

                    next_page = self.get_next_page(hxt)

    def get_next_page(self, hxt):
        return hxt.xpath('//div[@class="pagination-nav-buttons"]//a[text()="Next"]')


if __name__ == '__main__':
    st = StrideTite()
    st.run()



