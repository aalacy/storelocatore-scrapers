import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://goodoilcompany.com/locations"

        headers = {
            "Accept":"*/*",
            "X-Requested-With":"XMLHttpRequest",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding":"gzip, deflate, br"
        }

        body = requests.get("https://goodoilcompany.com/deal-signup/filter", headers=headers).text
        for result in [s.strip() for s in body.split('|')]:
            if result.strip():
                res_ = result.split('+')
                i = base.Item(result)
                i.add_value('locator_domain', base_url)
                i.add_value('page_url', base_url)
                i.add_value('location_name', res_[0], lambda x: x.strip())
                i.add_value('street_address', res_[2])
                i.add_value('city', res_[3])
                i.add_value('state', res_[4])
                i.add_value('zip', res_[5])
                i.add_value('longitude', res_[6])
                i.add_value('latitude', res_[7])
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
