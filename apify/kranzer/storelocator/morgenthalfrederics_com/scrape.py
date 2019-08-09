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
            st = result.get('streetaddress', '')
            addr = usaddress.parse(st)
            city = ' '.join([city[0] for city in addr if city[1] == "PlaceName"]).replace(',','')
            try:
                state = [state[0] for state in addr if state[1] == "StateName"][0].replace(',','')
                if state == 'US':
                    state = ''
            except:
                state = ''
            try:
                zip = [zip[0] for zip in addr if zip[1] == "ZipCode"][0].replace(',','')
                if len(zip) == 4:
                    zip = '0'+zip
            except:
                zip = ''
            street = st.replace(', {}, {} {}, US'.format(city, state, zip), '')
            i.add_value('city', city)
            i.add_value('state', state)
            i.add_value('zip', zip)
            i.add_value('country_code', "US")
            i.add_value('street_address', street)
            i.add_value('phone', result.get('phone','').strip())
            i.add_value('country_code', 'US')
            i.add_value('location_type', result.get('tags', '').strip())
            i.add_value('latitude', result.get('loc_lat',''))
            i.add_value('longitude', result.get('loc_long',''))
            i.add_value('store_number', result.get('id',''))
            yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
