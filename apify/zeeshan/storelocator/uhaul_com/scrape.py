import re 
import base
import requests

from zipdata import zipdata

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Uhaul(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'uhaul.com'
    seen = set()

    def map_data(self, row):

        address = row.get('address')
        city, state, zip_code = row.get('city'), row.get('state'), row.get('zip')
        geo = self.get_geo(address)
        
        location_name = xpath(row, '//a[@class="text-large"]//text()')
        location_type = xpath(row, '//small[@class="text-light"]//text()')

        street_address = address.replace('%s,%s %s' % (city.title(), state, zip_code,), '').strip()

        phone = xpath(row, '//a[contains(@href,"tel")]').text.strip()

        return {
            'locator_domain': self.domain_name
            ,'location_name': location_name
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zip_code
            ,'country_code': self.default_country
            ,'store_number': None
            ,'phone': phone
            ,'location_type': location_type
            ,'naics_code': None
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Host': 'www.uhaul.com'
            ,'Referer': 'https://www.uhaul.com/Locations/'
            ,'Upgrade-Insecure-Requests': '1'
            ,'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        })
        for data in zipdata:
            # https://www.uhaul.com/Locations/Brooklyn-NY-11230/Results/
            params = (data.city.title(), data.state, data.code,)
            url = 'https://www.uhaul.com/Locations/%s-%s-%s/Results/' % params
            request = session.get(url)
            if request.status_code == 200:
                hxt = html.fromstring(request.text)
                locations = hxt.xpath('//div[@id="locationsResults"]//ul//li')
                for location in locations:
                    
                    address = xpath(location, './/a[@class="address-link"]//@rel')

                    if address is None: continue

                    if address in self.seen: continue
                    else: self.seen.add(address)
                    
                    location.attrib['city'] = data.city
                    location.attrib['state'] = data.state
                    location.attrib['zip'] = data.code
                    location.attrib['address'] = address

                    yield location


if __name__ == '__main__':
    u = Uhaul()
    u.run()
