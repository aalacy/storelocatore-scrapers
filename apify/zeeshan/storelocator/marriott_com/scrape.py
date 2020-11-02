import base 
import requests
from lxml import html

from pdb import set_trace as bp

xpath = base.xpath

class Marriott(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'marriott.com'
    default_country = 'US'
    url = 'https://www.marriott.com/sitemap.us.hws.1.xml'

    def crawl(self):

        self.headers.update({
            'authority': 'www.marriott.com'
            ,'method': 'GET'
            ,'path': '/sitemap.us.hws.1.xml'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
        })

        r = requests.get(self.url, headers=self.headers)
        
        if r.status_code == 200:
            text = r.text.decode('utf-8').encode('ascii')
            hxt = html.fromstring(text)
            location_urls = html.fromstring(text).xpath('./url/loc/text()')
            for url in location_urls:
                r2 = requests.get(url, headers=self.headers)
                if r2.status_code == 200:
                    text = r2.text
                    hxt = html.fromstring(text)
                    image_source = xpath(hxt, "//div[contains(@class,'l-header-section')]//img/@src")
                    location_type = image_source.split('/')[5] if image_source else None
                    yield {
                        'locator_domain': self.domain_name
                        ,'location_name': xpath(hxt, '//span[@itemprop="name"]/text()')
                        ,'street_address': xpath(hxt, '//span[@itemprop="streetAddress"]/text()')
                        ,'city': xpath(hxt, '//span[@itemprop="addressLocality"]/text()')
                        ,'state': xpath(hxt, '//span[@itemprop="addressRegion"]/text()')
                        ,'zip': xpath(hxt, '//span[@itemprop="postalCode"]/text()')
                        ,'country_code': xpath(hxt, '//span[@itemprop="addressCountry"]/text()')
                        ,'store_number': None
                        ,'phone': xpath(hxt, '//span[@itemprop="telephone"]/text()')
                        ,'location_type': location_type
                        ,'naics_code': None 
                        ,'latitude': xpath(hxt, '//span[@itemprop="latitude"]/text()')
                        ,'longitude': xpath(hxt, '//span[@itemprop="longitude"]/text()')
                        ,'hours_of_operation': None
                    }

if __name__ == '__main__':
    m = Marriott()
    m.run()