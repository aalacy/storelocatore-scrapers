import re

import base
import requests, json
from urllib.parse import urljoin

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

            try:
                cszc = re.match(r'(?P<address>.+),(?P<city>.+?),\s(?P<state>[A-Z][A-Z])\s(?P<zip>\d+)?', result.get('streetaddress','')).groupdict()
                if cszc:
                    i.add_value('street_address', cszc.get('address'))
                    i.add_value('city', cszc.get('city'))
                    i.add_value('state', cszc.get('state'))
                    i.add_value('zip', cszc.get('zip'))
            except:
                pass
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
