import re
import base 
import requests
from lxml import html

from pdb import set_trace as bp

class BancorpSouth(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'www.bancorpsouth.com'
    default_country = 'US'
    state = None
    url = 'https://www.bancorpsouth.com/find-a-location'

    def _map_data(self, row):

        data = re.findall('\'([\.|A-Za-z0-9, <>-]+)\'', row)

        latitude, longitude, address, meta, _ = data

        postal_code = re.findall('\d{5}', address)
        postal_code = postal_code[0] if postal_code else None

        name, location_type = meta.split('<br>')
        location_type = location_type.strip()

        city = address.split(',')[-2].strip()

        address = ' '.join(address.split(',')[:-2])

        return {
            'locator_domain': self.domain_name
            ,'location_name': name
            ,'street_address': address
            ,'city': city
            ,'state': self.state.title()
            ,'zip': postal_code
            ,'country_code': self.default_country
            ,'store_number': None
            ,'phone': None
            ,'location_type': location_type
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
            ,'Cache-Control': 'max-age=0'
            ,'Connection': 'keep-alive'
            ,'Content-Type': 'application/x-www-form-urlencoded'
            ,'Host': self.domain_name
            ,'Origin': 'https://%s' % self.domain_name
            ,'Referer': self.url
            ,'Upgrade-Insecure-Requests': '1'
        })
        session = requests.Session()
        session.headers.update(self.headers)
        for state in self.us_states:
            self.state = state
            payload = {'location': state, 'location-type': 1}
            location = session.post(self.url, data=payload)
            if location.status_code == 200:
                location_hxt = html.fromstring(location.text)
                location_hxt.xpath('//div[@class="container"]//script[2]')
                javascript = location_hxt.xpath('//div[@class="container"]//script[2]')
                if javascript:
                    code = javascript[1].xpath('text()')
                    if code:
                        for row in code[0].split('\n'):
                            if 'setBranchMarkeronByLatLng' in row:
                                row = row.strip()
                                yield self._map_data(row)

if __name__ == '__main__':
    bs = BancorpSouth()
    bs.run()