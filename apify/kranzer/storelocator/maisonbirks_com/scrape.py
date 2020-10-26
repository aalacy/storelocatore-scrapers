import re
from string import capwords

import base
import requests, json
from urllib.parse import urljoin
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('maisonbirks_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://www.maisonbirks.com/en"
        # json_body = requests.post(base_url, data="curPage=1", headers={"accept": "application/json, text/javascript, */*; q=0.01",
        #                                                                "accept-encoding": "gzip, deflate, br",
        #                                                                "sec-fetch-mode": "cors",
        #                                                                "sec-fetch-site": "same-origin",
        #                                                                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36",
        #                                                                "x-requested-with": "XMLHttpReques",
        #                                                                "content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
        json_body = requests.get(base_url+'/storelocator/index/loadstore').json()
        for result in json_body.get('storesjson', []):
            if "USA" in result.get('address', '') or "US" in result.get('address', '') or "United States" in result.get('address', '') or "Canada" in result.get('address', ''):
                i = base.Item(result)
                href = result.get('rewrite_request_path', '')
                if href:
                    logger.info(href)
                    i.add_value('locator_domain', urljoin(base_url, href))
                    i.add_value('location_name', result.get('store_name',''))
                    i.add_value('location_type', result.get('store_type',''))
                    i.add_value('phone', result.get('phone',''))
                    i.add_value('latitude', result.get('latitude', ''))
                    i.add_value('longitude', result.get('longitude', ''))

                    addr_hours = self.get_addr(urljoin(base_url, href))
                    if not addr_hours:
                        continue
                    i.add_value('city', addr_hours['city'])
                    i.add_value('state', addr_hours['state'])
                    i.add_value('hours_of_operation', addr_hours['hours'])
                    i.add_value('street_address', addr_hours['address'])
                    i.add_value('country_code', base.get_country_by_code(capwords(addr_hours['state'])))
                    i.add_value('zip', addr_hours.get('zip'))
                    # logger.info(i)
                    yield i


    def get_addr(self, url):
        r = requests.get(url)
        selector = html.fromstring(r.text)
        data = {}
        valid = len(selector.xpath(
            '//table[preceding-sibling::h2[1][contains(text(), "Opening hours")]]//tr[not(td="Closed")]'))
        if valid == 0:
            return None
        address = selector.xpath('//div[@class="box-detail"]/p[preceding-sibling::h4[1][contains(text(), "Address")]]/span/span/text()')
        hours = selector.xpath('//table[preceding-sibling::h2[1][contains(text(), "Opening hours")]]//tr//text()')
        hours = [h.strip() for h in hours if h.strip()]
        hours = [s[:-1].strip()+':' if s[-1] == ':' else s for s in hours]
        z = lambda x: '; '.join([' '.join(x) for x in zip(x[0::2], x[1::2])]).replace('\n', '').strip()
        y =lambda x: x[2:] if x.startswith('; ') else x
        hours_st = y(z(hours))
        city_state = address[1]
        data['city'] = city_state.split(',')[0] or ''
        data['state'] = city_state.split(',')[1] or ''
        data['hours'] = hours_st or ''
        data['address'] = address[0][:address[0].find(', '+data['city'])] or ''
        logger.info(address[0])
        regex = r'{}, {},? (.+?),'.format(data['city'].replace('é','[é|e]'), base.get_state_code(capwords(data['state'])))
        logger.info(regex)
        zip_ = re.findall(regex, address[0])
        logger.info(zip_)
        if zip_:
            data['zip'] = zip_[0]
        logger.info(data)
        return data


if __name__ == '__main__':
    s = Scrape()
    s.run()
