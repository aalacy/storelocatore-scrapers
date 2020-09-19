import re
import base 
import requests
from lxml import html

from pdb import set_trace as bp


class Whywaitintheer(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'whywaitintheer.com'
    default_country = 'US'
    url = 'http://whywaitintheer.com/#'

    def _map_data(self, row):
        street_address, city, state, postal_code  = (None, None, None, None,)
        name, phone = (None, None,)

        address = row.xpath('//div[@id="address"]//p//text()')
        if address:
            street_address = ' '.join(address[:-1])
            street_address = re.sub('\s+', ' ', street_address)
            
            region = address[-1]
            street_address, region = street_address.strip(), region.strip()
            region_split = re.findall(r'[A-Za-z]+|[0-9]{5}', region)
            
            if region_split:
                state, postal_code = region_split[-2], region_split[-1]
                city = ' '.join(region_split[:-2])
            
        phone = row.xpath('//p[contains(text(), "Phone: ")]/text()')
        if phone:
            phone = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', phone[0])
            phone = phone[0] if phone else None

        hours_of_operation = row.xpath('//h2[contains(text(), "Phone and Hours")]/following-sibling::p[1]//text()')
        if hours_of_operation:
            hours_of_operation = ' '.join(hours_of_operation)
            hours_of_operation = re.sub('\s+', ' ', hours_of_operation)
            hours_of_operation = hours_of_operation.split('Hours: ')[-1]

        name = row.xpath('//h1//text()')
        name = name[0] if name else None
        name = name

        return {
            'locator_domain': self.domain_name
            ,'location_name': name
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': postal_code
            ,'country_code': self.default_country
            ,'store_number': None
            ,'phone': phone
            ,'location_type': None
            ,'naics_code': None 
            ,'latitude': None
            ,'longitude': None
            ,'hours_of_operation': hours_of_operation
        }

    def crawl(self):
        self.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Cache-Control': 'max-age=0'
            ,'Connection': 'keep-alive'
            ,'Host': 'whywaitintheer.com'
            ,'Upgrade-Insecure-Requests': '1'
        })
        session = requests.Session()
        session.headers.update(self.headers)
        homepage = session.get(self.url)
        if homepage.status_code == 200:
            homepage_hxt = html.fromstring(homepage.text)
            locations = homepage_hxt.xpath('//nav//a[contains(@href, "location")]/@href')
            for location_url in locations:
                location = session.get(location_url)
                if location.status_code == 200:
                    location_hxt = html.fromstring(location.text)
                    venues = location_hxt.xpath('//ul//li//a[@class="class_blue"]/@href')
                    for venue_url in venues:
                        venue = session.get(venue_url)
                        if venue.status_code == 200:
                            venue_hxt = html.fromstring(venue.text)
                            yield self._map_data(venue_hxt)

if __name__ == '__main__':
    w = Whywaitintheer()
    w.run()