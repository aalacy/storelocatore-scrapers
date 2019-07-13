import re
import base 
import requests
from lxml import html

from pdb import set_trace as bp


class ShopVersona(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'shopversona.com'
    url = 'https://www.shopversona.com/versonastores.cfm'

    def _map_data(self, row):
        street_address, city, state, postal_code  = (None, None, None, None,)
        latitude, longitude = (None, None,)
        phone = None
        
        metadata = row.xpath('text()')
        if metadata:
            street_address = metadata[2].strip()
            phone = metadata[3].strip()

        link = row.xpath('./a/@href')
        if link:
            link = link[0]
            query_params = base.query_params(link)
            latitude, longitude = query_params.get('sll', ',').split(',')
            address = query_params.get('daddr', None)
            if address:
                postal_code = re.findall('[0-9]{5}', address)
                if postal_code:
                    postal_code = postal_code[0]

        h4 = row.xpath('./h4/text()')
        if h4:
            h4 = h4[0].strip()
            city, state = h4.split(',')
            city = city.strip()
            state = state.strip()

        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('name')
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': postal_code
            ,'country_code': self.default_country
            ,'store_number': None
            ,'phone': phone
            ,'location_type': None
            ,'naics_code': None 
            ,'latitude': latitude
            ,'longitude': longitude
            ,'hours_of_operation': None
        }

    def crawl(self):
        self.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Host': 'www.shopversona.com'
            ,'Referer': self.url
            ,'Upgrade-Insecure-Requests': '1'
        })
        r1 = requests.get(self.url, headers=self.headers)
        if r1.status_code == 200:
            hxt1 = html.fromstring(r1.text)
            states = hxt1.xpath('//select[@name="locSt"]/option/@value')
            for state in states:
                query_params = {
                    'locRad': 100
                    ,'locZip': ''
                    ,'locSt': state
                }
                r2 = requests.get(self.url, params=query_params, headers=self.headers)
                if r2.status_code == 200:
                    hxt2 = html.fromstring(r2.text)
                    stores = hxt2.xpath('//div[@class="mapAddress"]')
                    for store in stores:
                        yield self._map_data(store)

if __name__ == '__main__':
    sv = ShopVersona()
    sv.run()