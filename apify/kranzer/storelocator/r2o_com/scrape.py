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
        base_url = "https://www.r2o.com"
        url = "https://www.r2o.com/application/ajax/stores_list.php"
        sel = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        for result in sel.json():
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', result.get("StorePageURL", ""), lambda x: urljoin(base_url, x) if x else None)
            i.add_value('location_name', result.get('StoreName', '').strip())
            i.add_value('street_address', [result.get('Address', ''), result.get('Address2', '')], lambda x: ', '.join([s.strip() for s in x if s]))
            i.add_value('city', result.get('City', '').strip())
            i.add_value('state', result.get('State', '').strip())
            i.add_value('zip', result.get('Zip', '').strip())
            i.add_value('phone', result.get('Phone', '').strip())
            i.add_value('country_code', base.get_country_by_code(i.as_dict().get('state')))
            i.add_value('latitude', result.get('Lat', ''))
            i.add_value('longitude', result.get('Long', ''))
            i.add_value('store_number', result.get('Store_ID',''))
            sel_ = base.selector(i.as_dict()['page_url'])
            i.add_value('hours_of_operation', sel_['tree'].xpath('(//div[@class="storehours"])[1]/p/text()'), lambda x: '; '.join(x))
            print(i)
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
