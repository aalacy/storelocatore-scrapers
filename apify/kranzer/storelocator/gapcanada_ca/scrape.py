import re
from string import capwords

import base
import ast
import requests, json
from urllib.parse import urljoin
from lxml import html
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.gapcanada.ca/customerService/info.do?cid=59182&mlink=39813,8953505,findStore_quickLinks&clink=8953505"

        headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }

        body = requests.get(base_url, headers=headers).text.replace('\n','')
        st = re.search(r'caStores=(\[.+\])</script>', body).group(1).replace('//','').strip().replace('],]','')
        strs = st.replace('[', '').split('],')
        for result in strs:
            result = result.replace(',,',',')
            res_ = ast.literal_eval('['+result+']')
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', base_url)
            i.add_value('location_name', res_[1], lambda x: x.strip())
            i.add_value('street_address', res_[2])
            i.add_value('city', res_[3])
            i.add_value('state', res_[4], lambda x: 'NL' if x=='NF' else x)
            i.add_value('zip', res_[5],
                        lambda x: x[:3]+' '+x[3:] if len(x) == 6 else x,
                        lambda x: 'V3B 7K5' if x == 'V3B SR5' else x)
            i.add_value('phone', res_[6])
            i.add_value('longitude', res_[-1])
            i.add_value('latitude', res_[-2])
            i.add_value('store_number', res_[0])
            i.add_value('location_type', 'WomenMenGapBodyAccessories')
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
