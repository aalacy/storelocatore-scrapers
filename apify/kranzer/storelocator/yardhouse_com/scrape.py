import re
from string import capwords

import base
import ast
import requests, json
from urllib.parse import urljoin
from lxml import html
from w3lib.html import remove_tags


class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.yardhouse.com/locations/all-locations?orderOnline=true"

        headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }

        body = html.fromstring(requests.get(base_url, headers=headers).text)
        # st = re.search(r'caStores=(\[.+\])</script>', body).group(1).replace('//','').strip().replace('],]','')
        # strs = st.replace('[', '').split('],')
        for id in body.xpath('//a[@id="locDetailsId"]/@href'):
            url = urljoin(base_url, id)
            id = id.split('/')[-1]
            result = requests.get('https://www.yardhouse.com/ajax/headerlocation.jsp?restNum={}'.format(id)).text
            res_ = ast.literal_eval(result)
            i = base.Item(result)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', url)
            i.add_value('location_name', res_[1], lambda x: x.strip())
            i.add_value('street_address', res_[3])
            i.add_value('city', res_[4])
            i.add_value('state', res_[5])
            i.add_value('zip', res_[6])
            i.add_value('phone', res_[7])
            i.add_value('longitude', res_[2].split('*')[1])
            i.add_value('latitude', res_[2].split('*')[0])
            i.add_value('store_number', id)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_value('hours_of_operation', res_[8], lambda x: x.replace('<br>', '; '), lambda x: remove_tags(x))
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
