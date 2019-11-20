import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
from w3lib.html import remove_tags

crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.mycdi.com/locations/"
        headers = {
            "Accept":"application/json, text/javascript, */*; q=0.01",
            "Content-Type":"application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }
        body = "action=get_procedures_list"
        json_body = requests.post("https://www.mycdi.com/wp-admin/admin-ajax.php", headers=headers, data=body).json()

        for result in json_body:
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', result.get('post_link'))
            i.add_value('location_name', result.get('post_title',''), lambda x: x.replace('&#8211;', '-'))
            i.add_value('phone', result.get('telephone_number',''))
            i.add_value('latitude', result.get('lat', ''))
            i.add_value('longitude', result.get('lng', ''))
            i.add_value('store_number', result.get('post_id',''))
            i.add_value('city', result.get('city', ''))
            i.add_value('state', result.get('state', ''))
            i.add_value('country_code', base.get_country_by_code(result.get('state','')))
            i.add_value('hours_of_operation', result.get('office_hours', ''),
                        lambda x: x.replace('\r\n<em>*Hours', '@@'),
                        lambda x: x.replace('\r\n<em>Hours', '@@'),
                        lambda x: x.replace('\r\n\r\n<em>Hours', '@@'),
                        lambda x: x.replace('\r\nHours', '@@'),
                        lambda x: x.replace('\r\n\r\n','@@'),
                        lambda x: remove_tags(x.split('@@')[0].replace('\n', '; ').replace('\r', '')))
            i.add_value('location_type', result.get('business_name',''))
            i.add_value('street_address', ' '.join([s for s in [result.get('street_address', ''), result.get('street_address_line_2','')] if s]))
            i.add_value('zip', result.get('zipcode', ''))
            if "coming soon" not in i.as_dict()['location_name'].lower() and i.as_dict()['street_address'] != "<MISSING>":
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
