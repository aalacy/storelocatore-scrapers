import re 
import base
import requests

from zipdata import zipdata

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class BarnesandNoble(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'bn.com'
    url = 'https://mstores.barnesandnoble.com/stores'
    seen = set()

    def get_store_id(self, location):
        store_id = xpath(location, './/a/@href')
        store_id = re.findall(r'[0-9]+', store_id)
        store_id = store_id[0] if store_id else None
        return store_id

    def map_data(self, row):
        
        text = etree.tostring(row)

        street_address = etree.tostring(xpath(row, './/h5[@class="nonoS"]//parent::*'))
        if street_address:
            street_address = street_address.split('</a> ')[-1]

        phone = re.findall(r'\d{3}-\d{3}-\d{4}', text)
        phone = phone[0] if phone else None

        city, state, zip_code = row.get('city'), row.get('state'), row.get('zip')

        address = '%s, %s, %s %s' % (street_address, city, state, zip_code)

        geo = self.get_geo(address)

        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/h5[@class="nonoS"]//text()')
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zip_code
            ,'country_code': self.default_country
            ,'store_number': self.get_store_id(row)
            ,'phone': phone
            ,'location_type': None
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
            ,'Host': 'mstores.barnesandnoble.com'
            ,'Referer': 'https://mstores.barnesandnoble.com/stores'
            ,'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

        })
        for data in zipdata:
            query_params = {
                'page': None
                ,'size': 100
                ,'searchText': data.code
                ,'storeFilter': 'all'
                ,'view': 'list'
                ,'v': 1
            }
            request = session.get(self.url, params=query_params)
            if request.status_code == 200:
                hxt = html.fromstring(request.text)
                locations = hxt.xpath('//div[@class="col-sm-12 col-md-8 col-lg-8 col-xs-12"]')
                for location in locations:

                    store_id = self.get_store_id(location)

                    if store_id in self.seen: continue
                    else: self.seen.add(store_id)
                        
                    location.attrib['city'] = data.city
                    location.attrib['state'] = data.state
                    location.attrib['zip'] = data.code

                    yield location


if __name__ == '__main__':
    bn = BarnesandNoble()
    bn.run()
