
import base
import requests, json
from urllib.parse import urljoin

class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.brookdale.com/bin/brookdale/community-search?care_type_category=resident&loc=&finrpt=&state={}"
        for state in base.us_states_codes:
            json_body = requests.get(base_url.format(state)).json()
            for result in json_body:
                href = result.get('website')
                if href:
                    i = base.Item(result)
                    i.add_value('locator_domain', href)
                    i.add_value('location_name', result.get('name','').strip())
                    i.add_value('street_address', result.get('address1','').strip())
                    i.add_value('store_number', result.get('business_unit_number','').strip())
                    i.add_value('city', result.get('city','').strip())
                    i.add_value('state', result.get('state','').strip())
                    i.add_value('zip', result.get('zip_postal_code','').strip(), lambda x: x[:5]+'-'+x[5:] if len(x) > 5 else x)
                    i.add_value('phone', result.get('phone_main','').strip())
                    i.add_value('country_code', result.get('country_code'))
                    i.add_value('latitude', result.get('latitude',''))
                    i.add_value('longitude', result.get('longitude',''))
                    yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
