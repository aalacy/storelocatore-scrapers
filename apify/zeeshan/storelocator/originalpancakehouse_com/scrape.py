import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class OriginalPancakeHouse(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'originalpancakehouse.com'
    url = 'http://originalpancakehouse.com'

    def map_data(self, row):
        name, address, city = row[0]
        link = xpath(html.fromstring(name), '//a')
        if link is not None:
            name = xpath(link, 'text()')

        name, address, city = name.strip(), address.strip(), city.strip()
        state, zipcode = row[1].split(' ')

        phone = row[2]

        geo_address = '%s, %s, %s %s' % (address, city, state, zipcode)
        geo = self.get_geo(geo_address)

        return {
            'locator_domain': self.domain_name
            ,'location_name': name
            ,'street_address': address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': None
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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like ,Gecko) Chrome/75.0.3770.100 Safari/537.36'
            ,'X-Requested-With': 'XMLHttpRequest'
        })
        locations_page = session.get('%s/locations.html' % self.url)
        if locations_page.status_code == 200:
            hxt = html.fromstring(locations_page.text)
            state_urls = hxt.xpath('//map[@name="phmapMap"]//area/@href')
            session.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
                ,'Accept-Encoding': 'gzip, deflate'
                ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
                ,'Connection': 'keep-alive'
                ,'Host': 'originalpancakehouse.com'
                ,'Upgrade-Insecure-Requests': '1'
            })
            for state_url in state_urls:
                state_page = session.get('%s/%s' % (self.url, state_url))
                if state_page.status_code == 200:
                    names_addresses = re.findall(r'<b>(.+)</b>.+\n +(.+)<br />\n +(.+),', state_page.text)
                    states_zips = re.findall(r'[A-Za-z]+ [0-9]{5}', state_page.text)
                    phones = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', state_page.text)
                    data = list(zip(names_addresses, states_zips, phones))
                    for row in data:
                        yield row


if __name__ == '__main__':
    oph = OriginalPancakeHouse()
    oph.run()
