import re

import base
import requests, json
from urllib.parse import urljoin
import usaddress

class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://morgenthalfrederics.com/pages/boutique-locator"
        json_body = requests.get("https://api.storepoint.co/v1/15bfcae8d5180e/locations?rq").json()
        for result in json_body.get('results', {}).get('locations',[]):
            working = ""
            for k, v in result.items():
                if k == "monday":
                    if v:
                        working+= "{} {};".format(k, v)
                if k == "tuesday":
                    if v:
                        working += "{} {};".format(k, v)
                if k == "wednesday":
                    if v:
                        working += "{} {};".format(k, v)
                if k == "thursday":
                    if v:
                        working += "{} {};".format(k, v)
                if k == "friday":
                    if v:
                        working += "{} {};".format(k, v)
                if k == "saturday":
                    if v:
                        working += "{} {};".format(k, v)
                if k == "sunday":
                    if v:
                        working += "{} {};".format(k, v)
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            if working:
                i.add_value('hours_of_operation', working)
            i.add_value('location_name', result.get('name','').strip())
            address = result.get('streetaddress', '')
            parsed = usaddress.tag(address)[0]
            city = 'Bal Harbour' if 'Bal Harbour, FL' in address else parsed.get("PlaceName", '<MISSING>')
            state = parsed.get('StateName', '<MISSING>')
            zip_code = '<MISSING>'
            try:
                zip_code = re.search(r' (\d{4,5}), US$', address).group(1)
            except:
                zip_code = parsed.get('ZipCode', '<MISSING>')
            country = 'US' if address.endswith('US') else parsed.get('CountryName', '<MISSING>')
            fixed_zip = '0{}'.format(zip_code) if len(zip_code) == 4 else zip_code

            street = self.parse_street(address, city, state, zip_code, country)

            i.add_value('city', city)
            i.add_value('state', state)
            i.add_value('zip', fixed_zip)
            i.add_value('country_code', country)
            i.add_value('street_address', street)
            i.add_value('phone', result.get('phone','').strip())
            i.add_value('location_type', result.get('tags', '').strip())
            i.add_value('latitude', result.get('loc_lat',''))
            i.add_value('longitude', result.get('loc_long',''))
            i.add_value('store_number', result.get('id',''))
            yield i

    def parse_street(self, address, city, state, zip_code, country):
        street = address
        if street.endswith(country): street = street[0:-1*len(country)].strip()
        if street.endswith(','): street = street[0:-1].strip()
        if street.endswith(zip_code): street = street[0:-1*len(zip_code)].strip()
        if street.endswith(state): street = street[0:-1*len(state)].strip()
        if street.endswith(','): street = street[0:-1].strip()
        if street.endswith('Bal Harbour'): street = street[0:-1*len('Bal Harbour')].strip()
        if street.endswith(city): street = street[0:-1*len(city)].strip()
        if street.endswith(','): street = street[0:-1].strip()
        return street

if __name__ == '__main__':
    s = Scrape()
    s.run()
