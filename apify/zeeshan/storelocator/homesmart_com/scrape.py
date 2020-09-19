import re 
import base
import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs
from lxml import (html, etree,)
from pdb import set_trace as bp

xpath = base.xpath

class HomeSmart(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'homesmart.com'
    url = 'https://homesmart.com/offices-agents-search/?cmd=search'

    def map_data(self, row):
        
        address, street_address, city, state, zipcode = None, None, None, None, None
        google_maps_url = str(xpath(row, './/a[@id="location"]//@href'))
        if google_maps_url:
            google_maps_url = google_maps_url.replace("#", "%23")
            query_params = parse_qs(urlparse.urlparse((google_maps_url)).query)
            address = str(query_params['q'])
            address_split = re.findall(r'(.+)  (.+) ([A-Z]{2}) ([0-9]{5})', address)
            if address_split:
                street_address, city, state, zipcode = address_split[0]
        geo = self.get_geo(address)
        office_number = None
        image_url = str(xpath(row, './/div[@id="office-photo"]//img//@src'))
        if image_url:
           office_number = image_url.split('/')[-1]

        phone_number = None
        phone_number_string = str(xpath(row, './/div[@id="office-contact"]//p[2]//text()'))
        if phone_number_string:
            phone_number = re.findall(r'(\([0-9]{3}\) [0-9]{3}-[0-9]{4})', phone_number_string)
            phone_number = phone_number[0] if phone_number else phone_number

        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/h3//text()').strip()
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': office_number
            ,'phone': phone_number
            ,'location_type': 'Office'
            ,'naics_code': None
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Host': 'homesmart.com'
            ,'Referer': 'https://homesmart.com/offices-agents-search/?cmd=search'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        })
        states_url = 'https://homesmart.com/api/v2/wordpress/json.get_states'
        states_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01'
            ,'X-Requested-With': 'XMLHttpRequest'
        }
        states_request = session.get(states_url, headers=states_headers)
        if states_request.status_code == 200:
            data = states_request.json()
            session.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
                ,'Accept-Encoding': 'gzip, deflate, br'

            })
            for code, _ in data.items():
                payload = {
                    'officeSearch': '' 
                    ,'state': code
                    ,'officeCity': ''
                    ,'button': ''
                }
                offices_request = session.post(self.url, data=payload)
                if offices_request.status_code == 200:
                    hxt = html.fromstring(offices_request.text)
                    offices_xpath = '//div[@id="results-container"]//div[@id="office-contatainer"]'
                    for office in hxt.xpath(offices_xpath):
                        yield office


if __name__ == '__main__':
    hs = HomeSmart()
    hs.run()
