import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
crawled = []

class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://snoozeeatery.com/locations"
        r = requests.get("https://snoozeeatery.com/wp-json/wp/v2/branches/?page=1&per_page=100", headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        body = r.json()
        for result in body:
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', result['link'])
            i.add_value('location_name', result['acf']['name'])
            i.add_value('phone', result['acf']['phone'])
            loc = result['acf']['address']['title']
            if loc:
                tup = re.findall(r'(.+?),(.+?),?\s([A-Z]+|California),?\s(\d+)', loc.replace('\r','').strip())
                if tup:
                    i.add_value('street_address', tup[0][0])
                    i.add_value('city', tup[0][1].strip())
                    i.add_value('state', tup[0][2])
                    i.add_value('zip', tup[0][3])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_value('latitude', result['acf']['coordinates']['latitude'])
            i.add_value('longitude', result['acf']['coordinates']['longitude'])
            i.add_value('hours_of_operation', result['acf']['hours'])
            i.add_value('store_number', result['id'])
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
