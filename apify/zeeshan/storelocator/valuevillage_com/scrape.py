import base 
import requests
import urllib.request, urllib.parse, urllib.error

from lxml import html
from pdb import set_trace as bp

xpath = base.xpath

class ValueVillage(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'valuevillage.com'
    url = 'https://maps.savers.com/api/getAutocompleteData'
    seen = set()

    def _map_data(self, row):

        hxt = html.fromstring(row.get('info', ''))

        location_type = None
        link = str(xpath(hxt, './/a[1]/@href'))
        if link:
            link = link.split('/')[-1]
            location_type = '-'.join(link.split('-')[:-1])

        csz = str(xpath(hxt, '//div[@class="csz"]//text()')) # Abbotsford, BC V2T 1V6 
        city, region_zip = csz.split(',')

        region_zip = region_zip.strip()
        region_zip_split = region_zip.split(' ')
        region = region_zip_split[0]
        postal_code = ' '.join(region_zip_split[1:])

        country_code = None
        country_code = 'US' if self.is_us_state(region) else country_code
        country_code = 'CA' if self.is_ca_province(region) else country_code

        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(hxt, '//a[@class="location-link gaq-link"]//@title')
            ,'street_address': xpath(hxt, '//div[@class="addr"]//text()')
            ,'city': city
            ,'state': region
            ,'zip': postal_code
            ,'country_code': country_code
            ,'store_number': row.get('locationId')
            ,'phone': xpath(hxt, '//div[@class="phone"]//text()')
            ,'location_type': location_type
            ,'naics_code': None 
            ,'latitude': row.get('lat')
            ,'longitude': row.get('lng')
            ,'hours_of_operation': None
        }

    def crawl(self):
        self.headers.update({
            'Accept': 'application/json, text/plain, */*'
            ,'Content-Type': 'application/json; charset=utf-8'
            ,'Referer': 'https://www.valuevillage.com'
        })
        r = requests.get(self.url, headers=self.headers)
        if r.status_code == 200:
            for keyword in r.json()['data']:
                search = urllib.parse.quote_plus(keyword)
                query_params = {
                    'template': 'search'
                    ,'level': 'search'
                    ,'radius': 100
                    ,'search': search

                }
                url = 'https://maps.savers.com/api/getAsyncLocations'
                self.headers.update({
                    'Accept': 'application/json, text/javascript, */*; q=0.01'
                    ,'Origin': 'https://stores.savers.com'
                    ,'Referer': 'https://stores.savers.com/search?q=%s&site=valuevillage&rad=100' % search
                })
                r2 = requests.get(url, params=query_params, headers=self.headers)
                if r2.status_code == 200:
                    locations = r2.json().get('markers')
                    if locations:
                        for location in locations:
                            location_id = location.get('locationId')
                            if location_id in self.seen:
                                continue
                            self.seen.add(location_id)
                            yield self._map_data(location)

if __name__ == '__main__':
    vv = ValueVillage()
    vv.run()
