import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.cdonepricecleaners.com/locations/"
        body = html.fromstring(requests.get(base_url).text).xpath('//div[@class="resp-tabs-container"]//script/text()')
        for result in body:
            json_resp = json.loads(result.strip()[:-1])
            i = base.Item(json_resp)
            i.add_value('locator_domain', base_url)
            i.add_value('location_name', json_resp['name'])
            i.add_value('phone', json_resp['telephone'])
            i.add_value('location_type', json_resp['@type'])
            i.add_value('latitude', json_resp['geo']['latitude'])
            i.add_value('longitude', json_resp['geo']['longitude'])
            i.add_value('city', json_resp['address']['addressLocality'])
            i.add_value('street_address', json_resp['address']['streetAddress'])
            i.add_value('state', json_resp['address']['addressRegion'])
            i.add_value('zip', json_resp['address']['postalCode'])
            i.add_value('country_code', json_resp['address']['addressCountry'])
            i.add_value('hours_of_operation', json_resp['openingHours'])
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
