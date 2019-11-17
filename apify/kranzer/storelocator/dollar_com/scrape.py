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
        base_url = "https://www.dollar.com/loc/"
        page = 1
        while True:
            json_body = requests.get("https://momentfeed-prod.apigee.net/api/llp.json?auth_token=TLKEBSULDKFABOUM&page={}".format(page)).json()
            if isinstance(json_body, list):
                for result in json_body:
                    i = base.Item(result)
                    result = result.get('store_info', {})
                    i.add_value('locator_domain', base_url)
                    i.add_value('page_url', result.get('website'))
                    i.add_value('location_name', result.get('name','') +' '+ result.get('locality',''))
                    i.add_value('phone', result.get('phone',''))
                    i.add_value('latitude', result.get('latitude', ''))
                    i.add_value('longitude', result.get('longitude', ''))
                    i.add_value('city', capwords(result.get('locality', '').replace('AP','')))
                    i.add_value('country_code', result.get('country', ''))
                    i.add_value('state', result.get('region', ''),
                                lambda x: 'QC' if x == 'QU' and i.as_dict()['country_code'] == 'CA' else x,
                                lambda x: 'MB' if x == 'MN' and i.as_dict()['country_code'] == 'CA' else x,
                                lambda x: 'AB' if x == 'AL' and i.as_dict()['country_code'] == 'CA' else x,
                                lambda x: 'SK' if x == 'SA' and i.as_dict()['country_code'] == 'CA' else x,
                                lambda x: 'ON' if x == 'OT' and i.as_dict()['country_code'] == 'CA' else x,
                                lambda x: 'NL' if x == 'NF' and i.as_dict()['country_code'] == 'CA' else x,)
                    i.add_value('zip', result.get('postcode', ''),
                                lambda x: x[:5] if len(x) > 5 and i.as_dict()['country_code'] == 'US' else x,
                                lambda x: '0'+x if len(x) == 4 else x)
                    i.add_value('hours_of_operation', self.get_hours(result.get('store_hours', '')))
                    i.add_value('street_address', ' '.join([s for s in [result.get('address', ''), result.get('address_3','')] if s]))
                    i.add_value('store_number', result.get('corporate_id', ''))
                    if i.as_dict()['country_code'] in {"US", "CA"}:
                        yield i
                page += 1
            else:
                break

    def get_hours(self, hours):
        mapper = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday",
            "7": "Sunday"
        }
        if hours:
            hours_st = ""
            h_ = [h for h in hours.split(';') if h.strip()]
            for h in h_:
                _ = h.split(',')
                hours_st += mapper[_[0]]+" "+_[1][:2]+':'+_[1][2:]+' - '+_[2][:2]+':'+_[2][2:]
                hours_st += '; '
            if hours_st.endswith('; '):
                hours_st = hours_st[:-2]
            return hours_st



if __name__ == '__main__':
    s = Scrape()
    s.run()
