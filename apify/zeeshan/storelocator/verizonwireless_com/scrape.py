import re
import base 
import json
import requests
from lxml import html
from pdb import set_trace as bp

xpath = base.xpath

class VerizonWireless(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'verizonwireless.com'
    url = 'https://es.verizonwireless.com/sitemap_storelocator.xml'

    def map_data(self, row):
        address = row.get('address', {})
        geo = row.get('geo', {})
        return {
            'locator_domain': self.domain_name
            ,'location_name': row.get('name')
            ,'street_address': address.get('streetAddress')
            ,'city': address.get('addressLocality')
            ,'state': address.get('addressRegion')
            ,'zip': address.get('postalCode')
            ,'country_code': address.get('addressCountry')
            ,'store_number': None
            ,'phone': row.get('telephone')
            ,'location_type': row.get('@type')
            ,'naics_code': None 
            ,'latitude': geo.get('latitude')
            ,'longitude': geo.get('longitude')
            ,'hours_of_operation': None
        }

    def crawl(self):
        
        self.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Host': 'en.verizonwireless.com'
        })

        r = requests.get(self.url, headers=self.headers)

        if r.status_code == 200:
            text = r.text.decode('utf-8').encode('ascii')
            hxt = html.fromstring(text)
            location_urls = hxt.xpath('//link[@hreflang="en-us"]/@href')
            del self.headers['Host']
            
            for url in location_urls:
                self.headers.update({
                    'authority': 'www.verizonwireless.com'
                    ,'method': 'GET'
                    ,'path': url.replace('https://www.verizonwireless.com', '')
                    ,'scheme': 'https'
                })
                

                r2 = requests.get(url, headers=self.headers)
                
                if r2.status_code == 200:
                    hxt2 = html.fromstring(r2.text)
                    data = xpath(hxt2, './/script[@type="application/ld+json"]/text()')
                    data = re.sub('\s+', '', data).replace('"{', '{').replace('}"', '}')
                    yield json.loads(data)

if __name__ == '__main__':
    vw = VerizonWireless()
    vw.run()
