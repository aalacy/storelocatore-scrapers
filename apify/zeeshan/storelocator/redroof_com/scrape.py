import base
import requests

from lxml import html

from pdb import set_trace as bp

xpath = base.xpath

class RedRoof(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'redroof.com'
    url = 'https://www.redroof.com/sitemap.xml'
    seen = set()

    def map_data(self, row):
        address = xpath(row, './/span[@itemprop="address"]/text()').strip()
        geo = self.get_geo(address)
        
        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/span[@itemprop="brand"]/text()').strip()
            ,'street_address': xpath(row, './/meta[@property="s:streetAddress"]/@content').strip()
            ,'city': xpath(row, './/meta[@property="s:addressLocality"]/@content').strip()
            ,'state': xpath(row, './/meta[@property="s:addressRegion"]/@content').strip()
            ,'zip': xpath(row, './/meta[@property="s:postalCode"]/@content').strip()
            ,'country_code': xpath(row, './/meta[@property="s:addressCountry"]/@content').strip()
            ,'store_number': row.store_number
            ,'phone': xpath(row, '//*[@itemprop="telephone"]/text()').strip()
            ,'location_type': xpath(row, './/span[@property="s:name"]/text()').strip()
            ,'naics_code': None
            ,'latitude': geo.get('lat')
            ,'longitude': geo.get('lng')
            ,'hours_of_operation': None
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'authority': 'www.redroof.com'
            ,'method': 'GET'
            ,'path': '/sitemap.xml'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'cache-control': 'max-age=0'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        })

        sitemap_page = session.get(self.url)
        hxt = html.fromstring(sitemap_page.text.decode('utf-8').encode('ascii'))
        property_links = hxt.xpath('//loc[contains(text(), "/property/")]/text()')

        for i, link in enumerate(property_links):

            link = link.lower()
            link = link[:-4] if link[-4:] == 'tile' else link
            if link in self.seen:
                continue
            self.seen.add(link)

            store_number = link.split('/')[-1]
            hotel_page = session.get(link)
            hotel_page_text = hotel_page.text
            hxt2 = html.fromstring(hotel_page_text)

            obj = xpath(hxt2, '//div[@class="c-content-block"]|//header[@class="header"]')

            if obj is None:
                continue

            setattr(obj, 'store_number', store_number)
            yield obj

if __name__ == '__main__':
    rr = RedRoof()
    rr.run()
