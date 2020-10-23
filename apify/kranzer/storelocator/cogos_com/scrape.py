import re
from string import capwords

import base
import ast
import requests, json
from urllib.parse import urljoin
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cogos_com')


class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://cogos.com/locations"

        headers = {
            "Accept":"*/*",
            "X-Requested-With":"XMLHttpRequest",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding":"gzip, deflate, br"
        }

        body = requests.get("https://cogos.com/locations/filter", headers=headers).text
        for result in [s.strip() for s in body.split('|')]:
            if result.strip():
                res_ = result.replace('&#8217;','\'').split('+')
                # logger.info(res_)
                i = base.Item(result)
                i.add_value('locator_domain', base_url)
                i.add_value('page_url', base_url)
                i.add_value('location_name', res_[0], lambda x: x.strip())
                i.add_value('street_address', res_[3])
                i.add_value('city', res_[4])
                i.add_value('state', res_[5])
                i.add_value('zip', res_[6])
                i.add_value('longitude', res_[7])
                i.add_value('latitude', res_[8])
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                try:
                    hours = ast.literal_eval(res_[10])
                    if hours['24/7'] == "Yes":
                        i.add_value('hours_of_operation', 'Open 24/7')
                except:
                    pass
                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
