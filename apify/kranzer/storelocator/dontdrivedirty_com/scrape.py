import time

import base
from lxml import html
import requests, json
from urllib.parse import urljoin

class Scrape(base.Spider):

    def crawl(self):

        body = "action=qq_ajax_map_first_run"
        base_url = "https://www.dontdrivedirty.com/wp-admin/admin-ajax.php"
        r = requests.post(base_url, data=body, headers={"origin":"https://www.dontdrivedirty.com",
                                                        "pragma":"no-cache",
                                                        "referer":"https://www.dontdrivedirty.com/",
                                                        "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                                                        "x-requested-with":"XMLHttpRequest",
                                                        "accept":"*/*",
                                                        "accept-encoding":"gzip, deflate, br",
                                                        "content-type":"application/x-www-form-urlencoded; charset=UTF-8"})

        for result in html.fromstring(r.text).xpath('//marker'):
            i = base.Item(result)
            if result.xpath('./@location_type')[0] == "1":
                i.add_value('locator_domain', "https://www.dontdrivedirty.com/locationsandpricing/")
                i.add_xpath('location_name', './@name', base.get_first)
                i.add_xpath('street_address', './@address', base.get_first)
                i.add_xpath('store_number', './@id', base.get_first)
                i.add_xpath('city', './@town', base.get_first)
                i.add_xpath('state', './@state', base.get_first)
                i.add_xpath('zip', './@zipcode', base.get_first)
                i.add_xpath('phone', './@phone', base.get_first)
                i.add_value('country_code', 'US')
                i.add_xpath('latitude', './@lat', base.get_first)
                i.add_xpath('longitude', './@lng', base.get_first)
                i.add_xpath('hours_of_operation', './@open | ./@close', lambda x: ' - '.join(x))
                yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
