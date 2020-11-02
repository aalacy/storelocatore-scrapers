import re 
import base
import random
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class NeuhausChocolate(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'neuhauschocolate.com'
    url = 'https://www.neuhauschocolate.com/en/store-locator.htm'

    def map_data(self, row):

        street_address = xpath(row, './/p/text()[preceding-sibling::br[4]]')
        if street_address:
            street_address = street_address.strip()

        city, state, zipcode = None, None, None
        region = xpath(row, './/p/text()[preceding-sibling::br[7]]')
        if region:
            region = region.strip()
            try:
                city, state_zip = region.split(',')
                state, zipcode = state_zip.strip().split(' ')
            except (ValueError, TypeError,):
                pass

        geo = {}
        if any([street_address, city, state, zipcode]):
            addess = '%s, %s, %s %s' % (street_address, city, state, zipcode)
            _geo = self.get_geo(street_address)
            if _geo:
                geo.update(_geo)

        hours_of_operation = [str(xpath(row, './/p/text()[preceding-sibling::br[%d]]' % i)) for i in (10,11)]
        if any(hours_of_operation):
            hours_of_operation = ', '.join(hours_of_operation)
            hours_of_operation = re.sub(r'\s+', ' ', hours_of_operation)
        else:
            hours_of_operation = ''

        phone = re.findall(r'\d+-\d+-\d+', str(etree.tostring(row)))
        phone = phone[0] if phone else None

        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/h3/text()[preceding-sibling::br]')
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': '<MISSING>'
            ,'phone': phone
            ,'location_type': '<MISSING>'
            ,'naics_code': '<MISSING>'
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': hours_of_operation or ''
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Cache-Control': 'max-age=0'
            ,'Connection': "keep-alive"
            ,'Host': 'www.neuhauschocolate.com'
            ,'Referer': 'https://www.neuhauschocolate.com/index-en.htm'
            ,'Upgrade-Insecure-Requests': "1"
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        })
        request = session.get(self.url)
        if request.status_code == 200:
            hxt = html.fromstring(request.text)
            locations = hxt.xpath('//div[@class="store"]')
            for location in locations:
                street_address = xpath(location, './/p/text()[preceding-sibling::br[4]]')
                if street_address:
                    yield location


if __name__ == '__main__':
    nc = NeuhausChocolate()
    nc.run()
