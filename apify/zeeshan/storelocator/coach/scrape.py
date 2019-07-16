import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Coach(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'www.coach.com'
    url = 'https://www.coach.com/on/demandware.store/Sites-Coach_US-Site/en_US/Stores-FilterResult'

    def map_data(self, row):

        address = xpath(row, './/div[@class="store-info"]/@data-address')
        geo = self.get_geo(address)
        
        country = xpath(row, './/span[@itemprop="addressCountry"]/text()')
        
        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/meta[@itemprop="name"]/@content')
            ,'street_address': xpath(row, './/span[@itemprop="streetAddress"]/text()')
            ,'city': xpath(row, './/span[@itemprop="addressLocality"]/text()')
            ,'state': xpath(row, './/span[@itemprop="addressRegion"]/text()')
            ,'zip': xpath(row, './/span[@itemprop="postalCode"]/text()')
            ,'country_code': self.country_code_lookup.get(country)
            ,'store_number': None
            ,'phone': xpath(row, './/span[@itemprop="telephone"]/text()')
            ,'location_type': None
            ,'naics_code': None
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': None
        }

    def crawl(self):

        session = requests.Session()

        session.headers.update({
            'authority': 'www.coach.com'
            ,'method': 'GET'
            ,'scheme': 'https'
            ,'accept': 'text/html, */*; q=0.01'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
            ,'x-requested-with': 'XMLHttpRequest'
        })

        query_params = {
            'firstQuery': 'AZ_state'
            ,'showRFStoreDivider': 'false'
            ,'showRStoreDivider': 'true'
            ,'showDStoreDivider': 'true'
            ,'showFStoreDivider': 'true'
            ,'start': '0'
            ,'sz': '10'
            ,'format': 'ajax'
            ,'instart_disable_injection': 'true'
        }

        for state in self.us_states_codes:

            query_params.update({
                'referer': 'https://www.coach.com/stores-edit-state?dwfrm_storelocator_address_states_stateUSSO=%s&dwfrm_storelocator_findbystate=Search+state' % state
            })
            
            start = 0
            offset = 10
            count = 10

            while start < count:

                query_params.update({
                    'firstQuery': '%s_state' % state
                    ,'start': start
                    ,'path': '/on/demandware.store/Sites-Coach_US-Site/en_US/Stores-FilterResult?firstQuery=%s_state&showRFStoreDivider=false&showRStoreDivider=true&showDStoreDivider=true&showFStoreDivider=true&start=%s&sz=10&format=ajax&instart_disable_injection=true' % (state, start,)
                })

                stores_page = session.get(self.url, params=query_params)
                hxt = html.fromstring(stores_page.text)

                count = eval(xpath(hxt, '//span[@class="newCount hide"]/text()'))
                start = start + offset

                stores = hxt.xpath('//div[@class="stores"]')
                for store in stores:
                    yield store


if __name__ == '__main__':
    c = Coach()
    c.run()
