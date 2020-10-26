import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = ["https://www.mathnasium.com/maps/maps/search?country=CAN",
                    "https://www.mathnasium.com/maps/maps/search?country=USA"]
        for b in base_url:
            sel = base.selector(b, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            _json = sel['tree'].xpath('//script[@type="text/javascript"]/text()[contains(., "locations = [{")]')[0]
            if _json:
                try:
                    js = re.findall(r'locations = (\[.+\])', _json)[0]
                    json_body = json.loads(js)
                    for j in json_body:
                        i = base.Item(j)
                        i.add_value('location_name', j['Map']['marker_text'])
                        i.add_value('locator_domain', b)
                        i.add_value('page_url', b)
                        i.add_value('phone', j['UserFranchise'].get('phone_number_1'))
                        i.add_value('latitude', j['Map']['latitude'])
                        i.add_value('longitude', j['Map']['longitude'])
                        i.add_value('street_address', j['Map'].get('street'))
                        i.add_value('city', j['Map'].get('city'))
                        i.add_value('state', j['Map'].get('state'))
                        i.add_value('zip', j['Map'].get('postal'), lambda x: x[:x.find(',')] if ',' in x else x)
                        i.add_value('country_code', base.get_country_by_code(j['Map'].get('state')))
                        if i.as_dict()['state'] != "USVI" and i.as_dict()['zip'] != "L05 2H2":
                            yield i
                except:
                    pass



if __name__ == '__main__':
    s = Scrape()
    s.run()
