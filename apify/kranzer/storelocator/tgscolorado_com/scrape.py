import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.tgscolorado.com/stores"
        json_body = json.loads(html.fromstring(requests.get(base_url).text).xpath('//script[@type="application/json"]/text()')[0])

        for result in json_body.get('hydrate', {}).get('locations', {}).get('view_fields', []):
            if result.get('field_store_is_active', '') == '1':
                i = base.Item(result)
                i.add_value('locator_domain', base_url)
                i.add_value('location_name', result.get('title',''))
                i.add_value('phone', result.get('field_store_phone',''))
                i.add_value('latitude', result.get('geolocation').get('lat', ''))
                i.add_value('longitude', result.get('geolocation').get('lng', ''))

                i.add_value('city', result.get('field_store_address_locality', ''))
                i.add_value('state', result.get('field_store_address_administrative_area', ''))
                i.add_value('country_code', result.get('field_store_address_country_code', ''))
                i.add_value('hours_of_operation', result.get('field_store_hours', ''))
                i.add_value('street_address', ', '.join([s for s in [result.get('field_store_address_address_line1', ''), result.get('field_store_address_address_line2','')] if s]))
                i.add_value('zip', result.get('field_store_address_postal_code', ''))
                i.add_value('store_number', result.get('field_store_id',''))
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
