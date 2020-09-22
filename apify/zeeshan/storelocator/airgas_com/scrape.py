import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Airgas(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'airgas.com'
    url = 'http://www.airgas.com/store-finder'

    def map_data(self, row):
        
        city, state, zipcode = None, None, None
        region = xpath(row, './/div[@class="map-information"]//p[5]//text()').strip()
        region_split = re.findall(r'([A-Za-z]+)\,([A-Z]{2})([0-9]{5})', region)
        if region_split:
            city, state, zipcode = region_split[0]

        phone = xpath(row, '//p[@class="findabranch_callout"]//text()')
        phone = re.sub(r'\s+|\|', '', phone)

        latitude, longitude = None, None
        geo_url = xpath(row, '//p[@class="findabranch_callout"]//a//@href')
        geo = re.findall(r'(-{0,1}\d{2}\.\d+)', geo_url)
        if geo:
            latitude, longitude = geo

        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/p[@class="location"]//text()').strip()
            ,'street_address': xpath(row, './/div[@class="map-information"]//p[3]//text()').strip()
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': None
            ,'phone': phone
            ,'location_type': 'Branch'
            ,'naics_code': None
            ,'latitude': latitude
            ,'longitude': longitude
            ,'hours_of_operation': None
        }

    def crawl(self):

        session = requests.Session()
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'Accept-Encoding': 'gzip, deflate'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Cache-Control': 'max-age=0'
            ,'Connection': 'keep-alive'
            ,'Content-Type': 'application/x-www-form-urlencoded'
            ,'Host': 'www.airgas.com'
            ,'Origin': 'http://www.airgas.com'
            ,'Referer': 'http://www.airgas.com/store-finder'
            ,'Upgrade-Insecure-Requests': '1'
            ,'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        })
        for state in self.us_states:
            payload = {
                'query': state
                ,'radius': 1000
                ,'type': 'BRANCH'
                ,'_requestConfirmationToken': 'eed8e9f8f7e5399041882152dee3af0b2c421c1c'
            }
            results_page = session.post(self.url, data=payload)
            hxt = html.fromstring(results_page.text)
            branches = hxt.xpath('//div[@class="col-xs-half directions-list"]//li')
            for branch in branches:
                yield branch


if __name__ == '__main__':
    a = Airgas()
    a.run()
